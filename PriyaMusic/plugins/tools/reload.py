import asyncio
import time

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.types import Message

from PriyaMusic import app
from PriyaMusic.core.call import Priya
from PriyaMusic.misc import db
from PriyaMusic.utils.database import get_assistant, get_authuser_names, get_cmode
from PriyaMusic.utils.decorators import AdminActual, language
from PriyaMusic.utils.formatters import alpha_to_int, get_readable_time
from config import BANNED_USERS, adminlist

_rel: dict = {}


@app.on_message(
    filters.command(["admincache", "reload", "refresh"]) & filters.group & ~BANNED_USERS
)
@language
async def reload_cache(client, message: Message, _):
    cid = message.chat.id
    try:
        saved = _rel.get(cid, 0)
        if saved and saved > time.time():
            left = get_readable_time(int(saved - time.time()))
            return await message.reply_text(_["reload_1"].format(left))

        adminlist[cid] = []
        async for member in app.get_chat_members(cid, filter=ChatMembersFilter.ADMINISTRATORS):
            if member.privileges and member.privileges.can_manage_video_chats:
                adminlist[cid].append(member.user.id)

        for user in await get_authuser_names(cid):
            uid = await alpha_to_int(user)
            adminlist[cid].append(uid)

        _rel[cid] = time.time() + 180
        await message.reply_text(_["reload_2"])
    except Exception:
        await message.reply_text(_["reload_3"])


@app.on_message(filters.command("reboot") & filters.group & ~BANNED_USERS)
@AdminActual
async def reboot_cmd(client, message: Message, _):
    mystic = await message.reply_text(_["reload_4"].format(app.mention))
    await asyncio.sleep(1)
    try:
        db[message.chat.id] = []
        await Priya.stop_stream_force(message.chat.id)
    except Exception:
        pass

    assistant_num = await get_assistant(message.chat.id)
    from PriyaMusic import userbot
    userbot_client = await userbot.get_client(assistant_num)
    if userbot_client:
        try:
            peer = message.chat.username or message.chat.id
            await userbot_client.resolve_peer(peer)
        except Exception:
            pass

    channel_id = await get_cmode(message.chat.id)
    if channel_id:
        try:
            db[channel_id] = []
            await Priya.stop_stream_force(channel_id)
        except Exception:
            pass

    await mystic.edit_text(_["reload_5"].format(app.mention))
