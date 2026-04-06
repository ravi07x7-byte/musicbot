from pyrogram.enums import MessageEntityType
from pyrogram.types import Message, User
from PriyaMusic import app


async def extract_user(m: Message) -> User | None:
    if m.reply_to_message and m.reply_to_message.from_user:
        return m.reply_to_message.from_user
    if not m.command or len(m.command) < 2:
        return None
    arg = m.command[1]
    try:
        entities = m.entities or []
        for ent in entities:
            if ent.type == MessageEntityType.TEXT_MENTION:
                return ent.user
        if arg.isdecimal():
            return await app.get_users(int(arg))
        return await app.get_users(arg)
    except Exception:
        return None
