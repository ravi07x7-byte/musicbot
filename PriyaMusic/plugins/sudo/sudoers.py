from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from PriyaMusic import app
from PriyaMusic.misc import SUDOERS
from PriyaMusic.utils.database import add_sudo, remove_sudo
from PriyaMusic.utils.decorators import language
from PriyaMusic.utils.extraction import extract_user
from config import BANNED_USERS, OWNER_ID


def _owner_only(mystic):
    async def wrapper(client, message: Message):
        if message.from_user.id != OWNER_ID:
            return await message.reply_text("⛔ Only the bot owner can use this.")
        return await mystic(client, message)
    return wrapper


@app.on_message(
    filters.command(["addsudo"],
                    prefixes=["/", "!", ".", "@", "#"])
    & filters.user(OWNER_ID)
)
@language
async def add_sudo_cmd(client, message: Message, _):
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text(_["general_1"])
    user = await extract_user(message)
    if not user:
        return await message.reply_text("User not found.")
    if user.id in SUDOERS:
        return await message.reply_text(_["sudo_1"].format(user.mention))
    if await add_sudo(user.id):
        SUDOERS.add(user.id)
        await message.reply_text(_["sudo_2"].format(user.mention))
    else:
        await message.reply_text(_["sudo_8"])


@app.on_message(
    filters.command(["delsudo", "rmsudo"],
                    prefixes=["/", "!", ".", "@", "#"])
    & filters.user(OWNER_ID)
)
@language
async def del_sudo_cmd(client, message: Message, _):
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text(_["general_1"])
    user = await extract_user(message)
    if not user:
        return await message.reply_text("User not found.")
    if user.id not in SUDOERS:
        return await message.reply_text(_["sudo_3"].format(user.mention))
    if await remove_sudo(user.id):
        SUDOERS.discard(user.id)
        await message.reply_text(_["sudo_4"].format(user.mention))
    else:
        await message.reply_text(_["sudo_8"])


@app.on_message(
    filters.command(["delallsudo"],
                    prefixes=["/", "!", ".", "@", "#"])
    & filters.user(OWNER_ID)
)
async def del_all_sudo_cmd(client, message: Message):
    removed = 0
    for uid in list(SUDOERS):
        if uid != OWNER_ID:
            if await remove_sudo(uid):
                SUDOERS.discard(uid)
                removed += 1
    await message.reply_text(f"✅ Removed {removed} sudo users.")


@app.on_message(
    filters.command(["sudolist", "listsudo", "sudoers"],
                    prefixes=["/", "!", ".", "@", "#"])
    & ~BANNED_USERS
)
async def sudolist_cmd(client, message: Message):
    kb = [[InlineKeyboardButton("👑 View Sudo List", callback_data="check_sudo_list")]]
    await message.reply_photo(
        photo="https://telegra.ph/file/d30d11c4365c025c25e3e.jpg",
        caption=(
            "» Check the sudo list via the button below.\n\n"
            "» Note: Only sudo users can view."
        ),
        reply_markup=InlineKeyboardMarkup(kb),
    )


@app.on_callback_query(filters.regex("^check_sudo_list$"))
async def check_sudo_cb(client, cq: CallbackQuery):
    if cq.from_user.id not in SUDOERS:
        return await cq.answer(
            "You are not a sudo user. Access denied.", show_alert=True
        )
    owner = await app.get_users(OWNER_ID)
    owner_mention = owner.mention
    caption = f"<b>Bot Moderators</b>\n\n🌹 Owner ➥ {owner_mention}\n\n"
    kb = [[InlineKeyboardButton("View Owner", url=f"tg://openmessage?user_id={OWNER_ID}")]]
    count = 1
    for uid in SUDOERS:
        if uid == OWNER_ID:
            continue
        try:
            u = await app.get_users(uid)
            caption += f"🎁 Sudo {count} » {u.mention}\n"
            kb.append([InlineKeyboardButton(
                f"View Sudo {count}", url=f"tg://openmessage?user_id={uid}"
            )])
            count += 1
        except Exception:
            continue
    kb.append([InlineKeyboardButton("◀ Back", callback_data="sudo_back")])
    await cq.message.edit_caption(caption=caption, reply_markup=InlineKeyboardMarkup(kb))


@app.on_callback_query(filters.regex("^sudo_back$"))
async def sudo_back_cb(client, cq: CallbackQuery):
    kb = [[InlineKeyboardButton("👑 View Sudo List", callback_data="check_sudo_list")]]
    await cq.message.edit_caption(
        caption="» Check the sudo list via the button below.\n\n» Note: Only sudo users can view.",
        reply_markup=InlineKeyboardMarkup(kb),
    )
