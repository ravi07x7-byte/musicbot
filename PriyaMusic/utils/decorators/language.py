from strings import get_string
from PriyaMusic import app
from PriyaMusic.misc import SUDOERS
from PriyaMusic.utils.database import get_lang, is_maintenance
import config


def language(mystic):
    async def wrapper(_, message, **kwargs):
        if not await is_maintenance():
            if message.from_user.id not in SUDOERS:
                return await message.reply_text(
                    f"{app.mention} is under maintenance. "
                    f'Visit <a href="{config.SUPPORT_CHAT}">support</a> for details.',
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
        return await mystic(_, message, _)
    return wrapper


def languageCB(mystic):
    async def wrapper(_, cq, **kwargs):
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
        return await mystic(_, cq, _)
    return wrapper


def LanguageStart(mystic):
    async def wrapper(_, message, **kwargs):
        try:
            lang = await get_lang(message.chat.id)
            _ = get_string(lang)
        except Exception:
            _ = get_string("en")
        return await mystic(_, message, _)
    return wrapper
