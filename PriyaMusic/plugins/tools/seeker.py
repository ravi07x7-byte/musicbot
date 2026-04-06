import asyncio

from PriyaMusic.misc import db
from PriyaMusic.utils.database import get_active_chats, is_music_playing


async def _track_timer():
    while True:
        await asyncio.sleep(1)
        try:
            for chat_id in await get_active_chats():
                if not await is_music_playing(chat_id):
                    continue
                playing = db.get(chat_id)
                if not playing:
                    continue
                duration = int(playing[0].get("seconds", 0))
                if duration == 0:
                    continue
                if db[chat_id][0]["played"] < duration:
                    db[chat_id][0]["played"] += 1
        except Exception:
            pass


asyncio.create_task(_track_timer())
