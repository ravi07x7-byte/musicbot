from pyrogram import filters
from pyrogram.types import Message

from PriyaMusic import app
from PriyaMusic.misc import SUDOERS
from PriyaMusic.utils.database import blacklist_chat, blacklisted_chats, whitelist_chat
from PriyaMusic.utils.decorators import language
from config import BANNED_USERS


@app.on_message(filters.command(["blacklistchat", "blchat"]) & SUDOERS)
@language
async def blchat_cmd(client, message: Message, _):
    if len(message.command) != 2:
        return await message.reply_text(_["black_1"])
    try:
        chat_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("Invalid chat ID.")
    if chat_id in await blacklisted_chats():
        return await message.reply_text(_["black_2"])
    await blacklist_chat(chat_id)
    await message.reply_text(_["black_3"])
    try:
        await app.leave_chat(chat_id)
    except Exception:
        pass


@app.on_message(filters.command(["whitelistchat", "unblchat"]) & SUDOERS)
@language
async def wlchat_cmd(client, message: Message, _):
    if len(message.command) != 2:
        return await message.reply_text(_["black_4"])
    try:
        chat_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("Invalid chat ID.")
    if chat_id not in await blacklisted_chats():
        return await message.reply_text(_["black_5"])
    await whitelist_chat(chat_id)
    await message.reply_text(_["black_6"])


@app.on_message(filters.command(["blacklistedchats", "blchats"]) & ~BANNED_USERS)
@language
async def blchats_cmd(client, message: Message, _):
    chats = await blacklisted_chats()
    if not chats:
        return await message.reply_text(_["black_8"].format(app.mention))
    text = _["black_7"]
    for i, cid in enumerate(chats, 1):
        try:
            title = (await app.get_chat(cid)).title
        except Exception:
            title = "Private Chat"
        text += f"{i}. {title} [<code>{cid}</code>]\n"
    await message.reply_text(text)
