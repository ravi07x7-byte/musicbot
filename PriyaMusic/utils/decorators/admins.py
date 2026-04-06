from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from PriyaMusic import app
from PriyaMusic.misc import SUDOERS, db
from PriyaMusic.utils.database import (
    get_authuser_names,
    get_cmode,
    get_lang,
    get_upvote_count,
    is_active_chat,
    is_maintenance,
    is_nonadmin_chat,
    is_skipmode,
)
from PriyaMusic.utils.formatters import int_to_alpha
from config import SUPPORT_CHAT, adminlist, confirmer
from strings import get_string


def AdminRightsCheck(mystic):
    async def wrapper(client, message):
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
        try:
            lang = await get_lang(message.chat.id)
            _ = get_string(lang)
        except Exception:
            _ = get_string("en")

        if message.sender_chat:
            upl = InlineKeyboardMarkup([[
                InlineKeyboardButton("How to fix?", callback_data="PriyaAdmin"),
            ]])
            return await message.reply_text(_["general_3"], reply_markup=upl)

        cmd = message.command[0]
        if cmd[0] == "c":
            chat_id = await get_cmode(message.chat.id)
            if chat_id is None:
                return await message.reply_text(_["setting_7"])
            try:
                await app.get_chat(chat_id)
            except Exception:
                return await message.reply_text(_["cplay_4"])
        else:
            chat_id = message.chat.id

        if not await is_active_chat(chat_id):
            return await message.reply_text(_["general_5"])

        if not await is_nonadmin_chat(message.chat.id):
            if message.from_user.id not in SUDOERS:
                admins = adminlist.get(message.chat.id, [])
                if message.from_user.id not in admins:
                    if await is_skipmode(message.chat.id):
                        upvote = await get_upvote_count(chat_id)
                        upl = InlineKeyboardMarkup([[
                            InlineKeyboardButton(
                                "Vote",
                                callback_data=f"ADMIN UpVote|{chat_id}_{cmd.title()}",
                            )
                        ]])
                        try:
                            vidid = db[chat_id][0]["vidid"]
                            file = db[chat_id][0]["file"]
                        except Exception:
                            return await message.reply_text(_["admin_14"])
                        senn = await message.reply_text(
                            f"Admin rights needed.\n{upvote} votes required.",
                            reply_markup=upl,
                        )
                        confirmer.setdefault(chat_id, {})[senn.id] = {
                            "vidid": vidid, "file": file
                        }
                        return
                    return await message.reply_text(_["admin_14"])

        return await mystic(client, message, _, chat_id)
    return wrapper


def AdminActual(mystic):
    async def wrapper(client, message):
        if not await is_maintenance():
            if message.from_user.id not in SUDOERS:
                return await message.reply_text(
                    f"{app.mention} is under maintenance.",
                    disable_web_page_preview=True,
                )
        try:
            await message.delete()
        except Exception:
            pass
        try:
            lang = await get_lang(message.chat.id)
            _ = get_string(lang)
        except Exception:
            _ = get_string("en")

        if message.sender_chat:
            upl = InlineKeyboardMarkup([[
                InlineKeyboardButton("How to fix?", callback_data="PriyaAdmin"),
            ]])
            return await message.reply_text(_["general_3"], reply_markup=upl)

        if message.from_user.id not in SUDOERS:
            try:
                member = (
                    await app.get_chat_member(message.chat.id, message.from_user.id)
                ).privileges
            except Exception:
                return
            if not member or not member.can_manage_video_chats:
                return await message.reply_text(_["general_4"])

        return await mystic(client, message, _)
    return wrapper


def ActualAdminCB(mystic):
    async def wrapper(client, cq):
        if not await is_maintenance():
            if cq.from_user.id not in SUDOERS:
                return await cq.answer(
                    f"{app.mention} is under maintenance.", show_alert=True
                )
        try:
            lang = await get_lang(cq.message.chat.id)
            _ = get_string(lang)
        except Exception:
            _ = get_string("en")

        if cq.message.chat.type == ChatType.PRIVATE:
            return await mystic(client, cq, _)

        if not await is_nonadmin_chat(cq.message.chat.id):
            try:
                a = (await app.get_chat_member(
                    cq.message.chat.id, cq.from_user.id
                )).privileges
            except Exception:
                return await cq.answer(_["general_4"], show_alert=True)
            if not a or not a.can_manage_video_chats:
                if cq.from_user.id not in SUDOERS:
                    token = await int_to_alpha(cq.from_user.id)
                    check = await get_authuser_names(cq.message.chat.id)
                    if token not in check:
                        return await cq.answer(_["general_4"], show_alert=True)

        return await mystic(client, cq, _)
    return wrapper
