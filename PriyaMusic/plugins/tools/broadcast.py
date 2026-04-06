import asyncio

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from PriyaMusic import app
from PriyaMusic.misc import SUDOERS
from PriyaMusic.utils.database import (
    get_authuser_names,
    get_served_chats,
    get_served_users,
)
from PriyaMusic.utils.decorators import language
from PriyaMusic.utils.formatters import alpha_to_int
from config import adminlist

IS_BROADCASTING = False


@app.on_message(filters.command("broadcast") & SUDOERS)
@language
async def broadcast_cmd(client, message: Message, _):
    global IS_BROADCASTING
    IS_BROADCASTING = True
    await message.reply_text(_["broad_1"])

    if message.reply_to_message:
        y = message.chat.id
        x = message.reply_to_message.id
        msg_text = None
    else:
        if len(message.command) < 2:
            IS_BROADCASTING = False
            return await message.reply_text(_["broad_2"])
        raw = message.text.split(None, 1)[1]
        for flag in ("-pin", "-nobot", "-pinloud", "-assistant", "-user"):
            raw = raw.replace(flag, "")
        msg_text = raw.strip()
        if not msg_text:
            IS_BROADCASTING = False
            return await message.reply_text(_["broad_8"])
        y = x = None

    flags = message.text

    # Bot broadcast
    if "-nobot" not in flags:
        sent, pinned = 0, 0
        for chat in await get_served_chats():
            cid = int(chat["chat_id"])
            try:
                if message.reply_to_message:
                    m = await app.forward_messages(cid, y, x)
                else:
                    m = await app.send_message(cid, msg_text)
                if "-pinloud" in flags:
                    await m.pin(disable_notification=False)
                    pinned += 1
                elif "-pin" in flags:
                    await m.pin(disable_notification=True)
                    pinned += 1
                sent += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                if fw.value <= 200:
                    await asyncio.sleep(fw.value)
            except Exception:
                continue
        try:
            await message.reply_text(_["broad_3"].format(sent, pinned))
        except Exception:
            pass

    # User broadcast
    if "-user" in flags:
        susr = 0
        for user in await get_served_users():
            uid = int(user["user_id"])
            try:
                if message.reply_to_message:
                    await app.forward_messages(uid, y, x)
                else:
                    await app.send_message(uid, msg_text)
                susr += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                if fw.value <= 200:
                    await asyncio.sleep(fw.value)
            except Exception:
                pass
        try:
            await message.reply_text(_["broad_4"].format(susr))
        except Exception:
            pass

    IS_BROADCASTING = False


async def _auto_admin_cache():
    from PriyaMusic.utils.database import get_active_chats
    while True:
        try:
            for cid in await get_active_chats():
                if cid not in adminlist:
                    adminlist[cid] = []
                    async for member in app.get_chat_members(
                        cid, filter=ChatMembersFilter.ADMINISTRATORS
                    ):
                        if member.privileges and member.privileges.can_manage_video_chats:
                            adminlist[cid].append(member.user.id)
                    for token in await get_authuser_names(cid):
                        uid = await alpha_to_int(token)
                        adminlist[cid].append(uid)
        except Exception:
            pass
        await asyncio.sleep(10)


import asyncio as _asyncio
_asyncio.create_task(_auto_admin_cache())
