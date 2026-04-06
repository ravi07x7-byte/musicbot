import random

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from PriyaMusic import app
from config import LOGGER_ID

PHOTOS = [
    "https://telegra.ph/file/1949480f01355b4e87d26.jpg",
    "https://telegra.ph/file/3ef2cc0ad2bc548bafb30.jpg",
    "https://telegra.ph/file/a7d663cd2de689b811729.jpg",
]


@app.on_message(filters.new_chat_members, group=2)
async def join_watcher(_, message: Message):
    chat = message.chat
    for member in message.new_chat_members:
        if member.id == app.id:
            try:
                link = await app.export_chat_invite_link(chat.id)
                count = await app.get_chat_members_count(chat.id)
                added_by = message.from_user.mention if message.from_user else "Unknown"
                msg = (
                    f"📝 <b>Bot added to a new group</b>\n\n"
                    f"📌 Name: {chat.title}\n"
                    f"🆔 ID: <code>{chat.id}</code>\n"
                    f"🔗 Username: @{chat.username or 'Private'}\n"
                    f"👥 Members: {count}\n"
                    f"➕ Added by: {added_by}"
                )
                await app.send_photo(
                    LOGGER_ID,
                    photo=random.choice(PHOTOS),
                    caption=msg,
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("Join Group 👀", url=link)
                    ]]),
                )
            except Exception:
                pass


@app.on_message(filters.left_chat_member)
async def left_watcher(_, message: Message):
    try:
        if message.left_chat_member.id != app.id:
            return
        removed_by = message.from_user.mention if message.from_user else "Unknown"
        text = (
            f"🚪 <b>Bot removed from group</b>\n\n"
            f"📌 Name: {message.chat.title}\n"
            f"🆔 ID: <code>{message.chat.id}</code>\n"
            f"❌ Removed by: {removed_by}"
        )
        await app.send_photo(LOGGER_ID, photo=random.choice(PHOTOS), caption=text)
    except Exception:
        pass
