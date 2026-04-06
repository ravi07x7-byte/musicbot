import asyncio
from datetime import datetime

from pyrogram.enums import ChatType

import config
from PriyaMusic import app
from PriyaMusic.core.call import Priya, autoend
from PriyaMusic.utils.database import get_active_chats, is_active_chat, is_autoend


async def _auto_leave():
    if not config.AUTO_LEAVING_ASSISTANT:
        return
    while True:
        await asyncio.sleep(900)
        try:
            from PriyaMusic import userbot
            from PriyaMusic.core.userbot import assistants
            for num in assistants:
                client = await userbot.get_client(num)
                if not client:
                    continue
                left = 0
                async for dialog in client.get_dialogs():
                    if dialog.chat.type in (ChatType.SUPERGROUP, ChatType.GROUP, ChatType.CHANNEL):
                        if dialog.chat.id in (config.LOGGER_ID,):
                            continue
                        if left >= 20:
                            break
                        if not await is_active_chat(dialog.chat.id):
                            try:
                                await client.leave_chat(dialog.chat.id)
                                left += 1
                            except Exception:
                                pass
        except Exception:
            pass


async def _auto_end():
    while True:
        await asyncio.sleep(5)
        if not await is_autoend():
            continue
        for chat_id, timer in list(autoend.items()):
            if not timer:
                continue
            if datetime.now() > timer:
                if not await is_active_chat(chat_id):
                    autoend.pop(chat_id, None)
                    continue
                autoend.pop(chat_id, None)
                try:
                    await Priya.stop_stream(chat_id)
                except Exception:
                    pass
                try:
                    await app.send_message(
                        chat_id,
                        "» Bot left the voice chat automatically — no one was listening.",
                    )
                except Exception:
                    pass


asyncio.create_task(_auto_leave())
asyncio.create_task(_auto_end())
