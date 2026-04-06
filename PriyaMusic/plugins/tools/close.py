import asyncio

from pyrogram import filters
from pyrogram.types import CallbackQuery

from PriyaMusic import app
from config import BANNED_USERS


@app.on_callback_query(filters.regex("^close$") & ~BANNED_USERS)
async def close_btn(_, cq: CallbackQuery):
    try:
        await cq.answer()
        await cq.message.delete()
        note = await cq.message.reply_text(f"Closed by {cq.from_user.mention}")
        await asyncio.sleep(2)
        await note.delete()
    except Exception:
        pass
