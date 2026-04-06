from typing import Union

from pyrogram import filters, types
from pyrogram.types import InlineKeyboardMarkup, Message

from PriyaMusic import app
from PriyaMusic.misc import SUDOERS
from PriyaMusic.utils.database import get_lang
from PriyaMusic.utils.decorators.language import LanguageStart, languageCB
from PriyaMusic.utils.inline import help_back_markup, help_pannel, private_help_panel
from config import BANNED_USERS, START_IMG_URL, SUPPORT_CHAT
from strings import get_string, helpers


@app.on_message(filters.command("help") & filters.private & ~BANNED_USERS)
@app.on_callback_query(filters.regex("settings_back_helper") & ~BANNED_USERS)
async def helper_private(client, update: Union[types.Message, types.CallbackQuery]):
    is_cb = isinstance(update, types.CallbackQuery)
    if is_cb:
        try:
            await update.answer()
        except Exception:
            pass
        lang = await get_lang(update.message.chat.id)
        _ = get_string(lang)
        await update.edit_message_text(
            _["help_1"].format(SUPPORT_CHAT),
            reply_markup=help_pannel(_, True),
        )
    else:
        try:
            await update.delete()
        except Exception:
            pass
        lang = await get_lang(update.chat.id)
        _ = get_string(lang)
        await update.reply_photo(
            photo=START_IMG_URL,
            has_spoiler=True,
            caption=_["help_1"].format(SUPPORT_CHAT),
            reply_markup=help_pannel(_),
        )


@app.on_message(filters.command("help") & filters.group & ~BANNED_USERS)
@LanguageStart
async def help_group(client, message: Message, _):
    kb = private_help_panel(_)
    await message.reply_text(_["help_2"], reply_markup=InlineKeyboardMarkup(kb))


@app.on_callback_query(filters.regex("^help_callback ") & ~BANNED_USERS)
@languageCB
async def help_cb(client, cq, _):
    cb = cq.data.split(None, 1)[1]
    kb = help_back_markup(_)

    help_map = {
        "hb1": helpers.HELP_1,
        "hb2": helpers.HELP_2,
        "hb3": helpers.HELP_3,
        "hb4": helpers.HELP_4,
        "hb5": helpers.HELP_5,
        "hb6": helpers.HELP_6,
        "hb7": helpers.HELP_7,
        "hb8": helpers.HELP_8,
        "hb9": helpers.HELP_9,
    }

    if cb == "hb7" and cq.from_user.id not in SUDOERS:
        return await cq.answer("This section is for sudo users only.", show_alert=True)

    text = help_map.get(cb)
    if text:
        await cq.answer()
        await cq.edit_message_text(text, reply_markup=kb)
