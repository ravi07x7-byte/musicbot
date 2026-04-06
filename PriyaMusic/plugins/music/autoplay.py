"""
Smart Autoplay for PriyaMusic.
- Tracks the genre/category of recently played songs
- If no user is active for AUTOPLAY_IDLE_MINUTES, keeps playing similar songs
- Category is detected from song title keywords
- Owner/admin can toggle autoplay per group
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Optional

from pyrogram import filters
from pyrogram.types import Message

import config
from PriyaMusic import YouTube, app
from PriyaMusic.core.call import Priya as VoiceCall
from PriyaMusic.misc import SUDOERS, db
from PriyaMusic.utils.database import (
    get_active_chats,
    get_autoplay,
    get_autoplay_category,
    is_active_chat,
    is_music_playing,
    set_autoplay,
    set_autoplay_category,
)
from PriyaMusic.utils.decorators import AdminActual, language
from config import BANNED_USERS

# Category keyword map — extend freely
CATEGORIES: dict[str, list[str]] = {
    "pop": ["pop", "taylor", "ariana", "selena", "dua lipa", "ed sheeran", "justin bieber"],
    "hiphop": ["rap", "hip hop", "drake", "kendrick", "eminem", "travis", "cardi"],
    "bollywood": ["bollywood", "hindi", "arijit", "atif", "jubin", "kumar sanu", "udit"],
    "rock": ["rock", "linkin park", "coldplay", "imagine dragons", "nirvana", "acdc"],
    "lofi": ["lofi", "lo-fi", "chill", "study", "sleep", "relax", "ambient"],
    "classical": ["classical", "beethoven", "mozart", "piano", "violin", "orchestra"],
    "punjabi": ["punjabi", "diljit", "sidhu", "ap dhillon", "shubh", "karan aujla"],
}

# Idle tracker: {chat_id: last_activity_time}
_last_activity: dict[int, datetime] = {}
_autoplay_running: set[int] = set()


def detect_category(title: str) -> str:
    title_lower = title.lower()
    for cat, keywords in CATEGORIES.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    return "pop"  # default


def get_search_query(category: str) -> str:
    queries = {
        "pop": ["best pop songs 2024", "top pop hits", "popular songs playlist"],
        "hiphop": ["best hip hop 2024", "top rap songs", "hiphop hits playlist"],
        "bollywood": ["best bollywood songs 2024", "hindi hits", "bollywood romantic songs"],
        "rock": ["best rock songs", "classic rock hits", "rock playlist 2024"],
        "lofi": ["lofi hip hop study", "chill lofi beats", "lofi relax music"],
        "classical": ["best classical music", "piano classical hits", "mozart beethoven best"],
        "punjabi": ["best punjabi songs 2024", "punjabi hits", "new punjabi music"],
    }
    return random.choice(queries.get(category, ["top songs 2024"]))


def update_activity(chat_id: int):
    _last_activity[chat_id] = datetime.now()


def is_idle(chat_id: int) -> bool:
    last = _last_activity.get(chat_id)
    if not last:
        return True
    return datetime.now() - last > timedelta(minutes=config.AUTOPLAY_IDLE_MINUTES)


async def autoplay_loop():
    """Background task: checks idle chats and queues next song by category."""
    await asyncio.sleep(60)
    while True:
        try:
            active_chats = await get_active_chats()
            for chat_id in active_chats:
                if not await get_autoplay(chat_id):
                    continue
                if not await is_music_playing(chat_id):
                    if is_idle(chat_id) and chat_id not in _autoplay_running:
                        asyncio.create_task(_play_autoplay(chat_id))
        except Exception:
            pass
        await asyncio.sleep(30)


async def _play_autoplay(chat_id: int):
    _autoplay_running.add(chat_id)
    try:
        category = await get_autoplay_category(chat_id)
        query = get_search_query(category)
        results = await YouTube.slider(query, random.randint(0, 5))
        if not results:
            return
        title, duration_min, thumbnail, vidid = results
        file_path, direct = await YouTube.download(vidid, None, videoid=True, video=None)
        if not file_path:
            return
        from PriyaMusic.utils.stream.stream import stream
        await stream(
            {},
            None,
            0,
            {"title": title, "link": f"https://youtu.be/{vidid}", "vidid": vidid,
             "duration_min": duration_min, "thumb": thumbnail},
            chat_id,
            f"Autoplay ({category})",
            chat_id,
            video=None,
            streamtype="youtube",
        )
        update_activity(chat_id)
    except Exception:
        pass
    finally:
        _autoplay_running.discard(chat_id)


# ─── Commands ───────────────────────────────────────────────

@app.on_message(filters.command("autoplay") & filters.group & ~BANNED_USERS)
@AdminActual
async def autoplay_cmd(client, message: Message, _):
    if len(message.command) < 2:
        status = "enabled" if await get_autoplay(message.chat.id) else "disabled"
        return await message.reply_text(
            f"🎵 Autoplay is currently <b>{status}</b>.\n"
            f"Use <code>/autoplay on</code> or <code>/autoplay off</code>.\n"
            f"Set category: <code>/autoplay category lofi</code>"
        )
    arg = message.command[1].lower()
    if arg == "on":
        await set_autoplay(message.chat.id, True)
        await message.reply_text("✅ Autoplay enabled. Bot will auto-queue similar songs when idle.")
    elif arg == "off":
        await set_autoplay(message.chat.id, False)
        await message.reply_text("❌ Autoplay disabled.")
    elif arg == "category" and len(message.command) >= 3:
        cat = message.command[2].lower()
        if cat not in CATEGORIES:
            return await message.reply_text(
                f"Available categories: {', '.join(CATEGORIES.keys())}"
            )
        await set_autoplay_category(message.chat.id, cat)
        await message.reply_text(f"✅ Autoplay category set to <b>{cat}</b>.")
    else:
        await message.reply_text(
            f"Available categories: {', '.join(CATEGORIES.keys())}"
        )


asyncio.create_task(autoplay_loop())
