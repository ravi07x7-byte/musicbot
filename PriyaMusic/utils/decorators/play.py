import asyncio

from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    InviteRequestSent,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from PriyaMusic import app
from PriyaMusic.misc import SUDOERS
from PriyaMusic.utils.database import (
    get_assistant,
    get_cmode,
    get_lang,
    get_playmode,
    get_playtype,
    is_active_chat,
    is_maintenance,
)
from PriyaMusic.utils.inline import botplaylist_markup
from config import PLAYLIST_IMG_URL, SUPPORT_CHAT, adminlist
from strings import get_string

_links: dict = {}


def PlayWrapper(command):
    async def wrapper(client, message):
        lang = await get_lang(message.chat.id)
        _ = get_string(lang)

        if message.sender_chat:
            upl = InlineKeyboardMarkup([[
                InlineKeyboardButton("How to fix?", callback_data="PriyaAdmin")
            ]])
            return await message.reply_text(_["general_3"], reply_markup=upl)

        if not await is_maintenance():
            if message.from_user.id not in SUDOERS:
                return await message.reply_text(
                    f"{app.mention} is under maintenance. "
                    f'<a href="{SUPPORT_CHAT}">Support</a>',
                    disable_web_page_preview=True,
                )

        try:
            await message.delete()
        except Exception:
            pass

        # Detect reply media
        reply = message.reply_to_message
        audio_tg = (reply.audio or reply.voice) if reply else None
        video_tg = (reply.video or reply.document) if reply else None

        from PriyaMusic import YouTube
        url = await YouTube.url(message)

        if not audio_tg and not video_tg and not url and len(message.command) < 2:
            buttons = botplaylist_markup(_)
            return await message.reply_photo(
                photo=PLAYLIST_IMG_URL,
                caption=_["play_18"],
                reply_markup=InlineKeyboardMarkup(buttons),
            )

        # Resolve channel play
        cmd = message.command[0]
        if cmd[0] == "c":
            chat_id = await get_cmode(message.chat.id)
            if chat_id is None:
                return await message.reply_text(_["setting_7"])
            try:
                chat = await app.get_chat(chat_id)
                channel = chat.title
            except Exception:
                return await message.reply_text(_["cplay_4"])
        else:
            chat_id = message.chat.id
            channel = None

        playmode = await get_playmode(message.chat.id)
        playty = await get_playtype(message.chat.id)

        # Playtype check
        if playty != "Everyone":
            if message.from_user.id not in SUDOERS:
                admins = adminlist.get(message.chat.id, [])
                if message.from_user.id not in admins:
                    return await message.reply_text(_["play_4"])

        # Video flag
        video = None
        if cmd[0] == "v" or (len(cmd) > 1 and cmd[1] == "v"):
            video = True
        elif "-v" in message.text:
            video = True

        # Force play flag
        fplay = True if cmd.endswith("e") else None
        if fplay and not await is_active_chat(chat_id):
            return await message.reply_text(_["play_16"])

        # Join assistant if not in chat
        if not await is_active_chat(chat_id):
            assistant_num = await get_assistant(chat_id)
            from PriyaMusic import userbot
            userbot_client = await userbot.get_client(assistant_num)
            if not userbot_client:
                return await message.reply_text("No assistant available.")

            try:
                await app.get_chat_member(chat_id, userbot_client.id)
            except UserNotParticipant:
                invite = _links.get(chat_id)
                if not invite:
                    if message.chat.username:
                        invite = message.chat.username
                        try:
                            await userbot_client.resolve_peer(invite)
                        except Exception:
                            pass
                    else:
                        try:
                            invite = await app.export_chat_invite_link(chat_id)
                        except ChatAdminRequired:
                            return await message.reply_text(_["call_1"])
                        except Exception as e:
                            return await message.reply_text(
                                _["general_2"].format(type(e).__name__)
                            )

                if invite and invite.startswith("https://t.me/+"):
                    invite = invite.replace("https://t.me/+", "https://t.me/joinchat/")

                myu = await message.reply_text(_["call_4"].format(app.mention))
                try:
                    await asyncio.sleep(1)
                    await userbot_client.join_chat(invite)
                except InviteRequestSent:
                    try:
                        await app.approve_chat_join_request(chat_id, userbot_client.id)
                    except Exception as e:
                        return await message.reply_text(
                            _["general_2"].format(type(e).__name__)
                        )
                    await asyncio.sleep(3)
                    await myu.edit(_["call_5"].format(app.mention))
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    return await message.reply_text(
                        _["general_2"].format(type(e).__name__)
                    )

                _links[chat_id] = invite
                try:
                    await userbot_client.resolve_peer(chat_id)
                except Exception:
                    pass
            except Exception:
                pass

        return await command(
            client, message, _, chat_id, video, channel, playmode, url, fplay
        )

    return wrapper
