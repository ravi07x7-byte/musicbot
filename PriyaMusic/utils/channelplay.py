from PriyaMusic import app
from PriyaMusic.utils.database import get_cmode


async def get_channeplayCB(_, command: str, CallbackQuery):
    if command == "c":
        chat_id = await get_cmode(CallbackQuery.message.chat.id)
        if chat_id is None:
            try:
                await CallbackQuery.answer(_["setting_7"], show_alert=True)
            except Exception:
                pass
            raise Exception("No channel mode set")
        try:
            channel = (await app.get_chat(chat_id)).title
        except Exception:
            try:
                await CallbackQuery.answer(_["cplay_4"], show_alert=True)
            except Exception:
                pass
            raise Exception("Cannot get channel")
    else:
        chat_id = CallbackQuery.message.chat.id
        channel = None
    return chat_id, channel
