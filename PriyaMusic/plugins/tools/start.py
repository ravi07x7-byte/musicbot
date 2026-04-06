import time

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardMarkup, Message

import config
from PriyaMusic import app
from PriyaMusic.misc import _boot_
from PriyaMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from PriyaMusic.utils.decorators.language import LanguageStart
from PriyaMusic.utils.formatters import get_readable_time
from PriyaMusic.utils.inline.start import private_panel, start_panel
from config import BANNED_USERS
from strings import get_string


@app.on_message(filters.command("start") & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)

    if len(message.text.split()) > 1:
        arg = message.text.split(None, 1)[1]

        if arg.startswith("help"):
            from PriyaMusic.utils.inline.help import help_pannel
            return await message.reply_photo(
                photo=config.START_IMG_URL,
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=help_pannel(_),
                has_spoiler=True,
            )

    out = private_panel(_)
    await message.reply_photo(
        photo=config.START_IMG_URL,
        caption=_["start_2"].format(message.from_user.mention, app.mention),
        reply_markup=InlineKeyboardMarkup(out),
        has_spoiler=True,
    )
    if await is_on_off(2):
        await app.send_message(
            config.LOGGER_ID,
            f"{message.from_user.mention} started the bot.\n"
            f"ID: <code>{message.from_user.id}</code>\n"
            f"Username: @{message.from_user.username}",
        )


@app.on_message(filters.command("start") & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_group(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    await message.reply_photo(
        photo=config.START_IMG_URL,
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
        has_spoiler=True,
    )
    await add_served_chat(message.chat.id)


@app.on_message(filters.new_chat_members, group=-1)
async def on_new_member(client, message: Message):
    for member in message.new_chat_members:
        try:
            lang = await get_lang(message.chat.id)
            _ = get_string(lang)

            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except Exception:
                    pass
                continue

            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)

                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                await message.reply_photo(
                    config.START_IMG_URL,
                    caption=_["start_3"].format(
                        message.from_user.first_name,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                    has_spoiler=True,
                )
                await add_served_chat(message.chat.id)
        except Exception as e:
            print(e)
