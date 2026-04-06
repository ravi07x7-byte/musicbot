from pyrogram.enums import ParseMode
from PriyaMusic import app
from PriyaMusic.utils.database import is_on_off
from config import LOGGER_ID


async def play_logs(message, streamtype: str):
    if not await is_on_off(2):
        return
    if message.chat.id == LOGGER_ID:
        return
    try:
        text = (
            f"<b>{app.mention} Play Log</b>\n\n"
            f"<b>Chat ID:</b> <code>{message.chat.id}</code>\n"
            f"<b>Chat:</b> {message.chat.title}\n"
            f"<b>Username:</b> @{message.chat.username}\n\n"
            f"<b>User ID:</b> <code>{message.from_user.id}</code>\n"
            f"<b>Name:</b> {message.from_user.mention}\n"
            f"<b>Username:</b> @{message.from_user.username}\n\n"
            f"<b>Query:</b> {message.text.split(None, 1)[1] if len(message.text.split()) > 1 else 'N/A'}\n"
            f"<b>Type:</b> {streamtype}"
        )
        await app.send_message(
            chat_id=LOGGER_ID,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except Exception:
        pass
