"""
Smart ban system for PriyaMusic.
Modes:
  /ban        — ban a replied/mentioned user
  /sban       — scan group: show deleted & real accounts; owner selects
  /gban       — global ban across all served chats
  /dban       — ban only deleted (deactivated) accounts in the group
"""

import asyncio

from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

import config
from PriyaMusic import app
from PriyaMusic.misc import SUDOERS
from PriyaMusic.utils.database import (
    add_banned_user,
    get_served_chats,
    is_banned_user,
    remove_banned_user,
)
from PriyaMusic.utils.decorators import AdminActual, language
from PriyaMusic.utils.extraction import extract_user
from PriyaMusic.utils.security import alert_owner
from config import BANNED_USERS


# ─── /ban ───────────────────────────────────────────────────
@app.on_message(filters.command("ban") & filters.group & ~BANNED_USERS)
@AdminActual
async def ban_user(client, message: Message, _):
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("Reply to a user or provide username/id.")
    user = await extract_user(message)
    if not user:
        return await message.reply_text("Could not find user.")
    if user.id == message.from_user.id:
        return await message.reply_text("You can't ban yourself.")
    if user.id in SUDOERS:
        return await message.reply_text("Can't ban a sudo user.")
    try:
        await message.chat.ban_member(user.id)
        await message.reply_text(
            f"✅ {user.mention} has been banned.\n"
            f"Banned by: {message.from_user.mention}"
        )
        await alert_owner(
            f"🔨 Ban action\n"
            f"Chat: {message.chat.title} (<code>{message.chat.id}</code>)\n"
            f"User: {user.mention} (<code>{user.id}</code>)\n"
            f"By: {message.from_user.mention}"
        )
    except Exception as e:
        await message.reply_text(f"Failed to ban: {e}")


# ─── /unban ─────────────────────────────────────────────────
@app.on_message(filters.command("unban") & filters.group & ~BANNED_USERS)
@AdminActual
async def unban_user(client, message: Message, _):
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("Reply to a user or provide username/id.")
    user = await extract_user(message)
    if not user:
        return await message.reply_text("Could not find user.")
    try:
        await message.chat.unban_member(user.id)
        await message.reply_text(f"✅ {user.mention} has been unbanned.")
    except Exception as e:
        await message.reply_text(f"Failed to unban: {e}")


# ─── /dban — delete all deactivated accounts ────────────────
@app.on_message(filters.command("dban") & filters.group & ~BANNED_USERS)
@AdminActual
async def dban(client, message: Message, _):
    msg = await message.reply_text("🔍 Scanning for deleted accounts...")
    deleted = []
    async for member in app.get_chat_members(message.chat.id):
        if member.user.is_deleted:
            deleted.append(member.user.id)

    if not deleted:
        return await msg.edit_text("No deleted accounts found.")

    await msg.edit_text(f"Found {len(deleted)} deleted accounts. Banning...")
    banned = 0
    for uid in deleted:
        try:
            await message.chat.ban_member(uid)
            banned += 1
            await asyncio.sleep(0.3)
        except Exception:
            continue
    await msg.edit_text(f"✅ Banned {banned} deleted accounts.")
    await alert_owner(
        f"🗑 /dban executed\n"
        f"Chat: {message.chat.title} (<code>{message.chat.id}</code>)\n"
        f"Deleted accounts banned: {banned}\n"
        f"By: {message.from_user.mention}"
    )


# ─── /sban — smart scan with selection ──────────────────────
_scan_cache: dict[int, dict] = {}


@app.on_message(filters.command("sban") & filters.group & ~BANNED_USERS)
@AdminActual
async def smart_ban(client, message: Message, _):
    msg = await message.reply_text("🔍 Scanning group members...")
    deleted = []
    real = []

    async for member in app.get_chat_members(message.chat.id):
        u = member.user
        if u.is_deleted:
            deleted.append(u)
        elif not u.is_bot:
            real.append(u)

    _scan_cache[message.chat.id] = {"deleted": deleted, "real": real}

    text = (
        f"📊 <b>Scan complete for {message.chat.title}</b>\n\n"
        f"🗑 Deleted accounts: <b>{len(deleted)}</b>\n"
        f"👤 Real accounts: <b>{len(real)}</b>\n\n"
        f"Choose an action:"
    )
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🗑 Ban Deleted", callback_data=f"sban_deleted_{message.chat.id}"),
            InlineKeyboardButton("👤 Select & Ban", callback_data=f"sban_select_{message.chat.id}"),
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data="sban_cancel")],
    ])
    await msg.edit_text(text, reply_markup=buttons)


@app.on_callback_query(filters.regex(r"^sban_deleted_(-?\d+)$"))
async def sban_deleted_cb(client, cq: CallbackQuery):
    chat_id = int(cq.data.split("_")[-1])
    if cq.from_user.id not in SUDOERS:
        member = await app.get_chat_member(chat_id, cq.from_user.id)
        if not member.privileges or not member.privileges.can_restrict_members:
            return await cq.answer("You don't have ban rights.", show_alert=True)

    cache = _scan_cache.get(chat_id, {})
    deleted = cache.get("deleted", [])
    if not deleted:
        return await cq.answer("No deleted accounts found.", show_alert=True)

    await cq.edit_message_text(f"Banning {len(deleted)} deleted accounts...")
    banned = 0
    for u in deleted:
        try:
            await app.ban_chat_member(chat_id, u.id)
            banned += 1
            await asyncio.sleep(0.3)
        except Exception:
            continue
    _scan_cache.pop(chat_id, None)
    await cq.edit_message_text(f"✅ Banned {banned} deleted accounts.")
    await alert_owner(
        f"🗑 Smart ban: deleted accounts\n"
        f"Chat: <code>{chat_id}</code> | Banned: {banned}\n"
        f"By: {cq.from_user.mention}"
    )


@app.on_callback_query(filters.regex(r"^sban_select_(-?\d+)$"))
async def sban_select_cb(client, cq: CallbackQuery):
    chat_id = int(cq.data.split("_")[-1])
    cache = _scan_cache.get(chat_id, {})
    real = cache.get("real", [])[:20]  # show first 20

    if not real:
        return await cq.answer("No real accounts found.", show_alert=True)

    buttons = []
    for u in real:
        name = (u.first_name or "")[:20]
        buttons.append([InlineKeyboardButton(
            f"🔨 {name} ({u.id})",
            callback_data=f"sban_do_{chat_id}_{u.id}"
        )])
    buttons.append([InlineKeyboardButton("❌ Done", callback_data="sban_cancel")])
    await cq.edit_message_text("Select a user to ban:", reply_markup=InlineKeyboardMarkup(buttons))


@app.on_callback_query(filters.regex(r"^sban_do_(-?\d+)_(-?\d+)$"))
async def sban_do_cb(client, cq: CallbackQuery):
    parts = cq.data.split("_")
    chat_id, user_id = int(parts[2]), int(parts[3])
    try:
        await app.ban_chat_member(chat_id, user_id)
        await cq.answer(f"Banned {user_id}.", show_alert=True)
        await alert_owner(
            f"🔨 Selective ban\n"
            f"Chat: <code>{chat_id}</code> | User: <code>{user_id}</code>\n"
            f"By: {cq.from_user.mention}"
        )
    except Exception as e:
        await cq.answer(f"Failed: {e}", show_alert=True)


@app.on_callback_query(filters.regex("^sban_cancel$"))
async def sban_cancel_cb(client, cq: CallbackQuery):
    await cq.edit_message_text("Action cancelled.")


# ─── /gban ──────────────────────────────────────────────────
@app.on_message(filters.command("gban") & SUDOERS)
@language
async def gban(client, message: Message, _):
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("Reply or provide user.")
    user = await extract_user(message)
    if not user or user.id in SUDOERS:
        return await message.reply_text("Cannot gban this user.")
    if await is_banned_user(user.id):
        return await message.reply_text(f"{user.mention} is already gbanned.")
    BANNED_USERS.add(user.id)
    chats = [int(c["chat_id"]) for c in await get_served_chats()]
    msg = await message.reply_text(f"Gbanning {user.mention} from {len(chats)} chats...")
    banned = 0
    for cid in chats:
        try:
            await app.ban_chat_member(cid, user.id)
            banned += 1
        except FloodWait as fw:
            await asyncio.sleep(fw.value)
        except Exception:
            continue
    await add_banned_user(user.id)
    await msg.edit_text(f"✅ Gbanned {user.mention} from {banned} chats.")
    await alert_owner(
        f"🌐 Global ban\n"
        f"User: {user.mention} (<code>{user.id}</code>)\n"
        f"Chats: {banned}\nBy: {message.from_user.mention}"
    )


@app.on_message(filters.command("ungban") & SUDOERS)
@language
async def ungban(client, message: Message, _):
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("Reply or provide user.")
    user = await extract_user(message)
    if not await is_banned_user(user.id):
        return await message.reply_text(f"{user.mention} is not gbanned.")
    BANNED_USERS.discard(user.id)
    chats = [int(c["chat_id"]) for c in await get_served_chats()]
    msg = await message.reply_text(f"Ungbanning {user.mention}...")
    unbanned = 0
    for cid in chats:
        try:
            await app.unban_chat_member(cid, user.id)
            unbanned += 1
        except FloodWait as fw:
            await asyncio.sleep(fw.value)
        except Exception:
            continue
    await remove_banned_user(user.id)
    await msg.edit_text(f"✅ Ungbanned {user.mention} from {unbanned} chats.")
