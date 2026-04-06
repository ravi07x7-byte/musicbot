import asyncio
from typing import Union

from PriyaMusic.misc import db
from PriyaMusic.utils.formatters import check_duration, seconds_to_min
from config import autoclean, time_to_seconds


async def put_queue(
    chat_id: int,
    original_chat_id: int,
    file: str,
    title: str,
    duration: str,
    user: str,
    vidid: str,
    user_id: int,
    stream: str,
    forceplay: Union[bool, str] = None,
):
    title = title.title()
    try:
        duration_sec = max(0, time_to_seconds(duration) - 3)
    except Exception:
        duration_sec = 0

    item = {
        "title": title,
        "dur": duration,
        "streamtype": stream,
        "by": user,
        "user_id": user_id,
        "chat_id": original_chat_id,
        "file": file,
        "vidid": vidid,
        "seconds": duration_sec,
        "played": 0,
    }

    if forceplay:
        existing = db.get(chat_id)
        if existing:
            existing.insert(0, item)
        else:
            db[chat_id] = [item]
    else:
        db.setdefault(chat_id, []).append(item)

    autoclean.append(file)


async def put_queue_index(
    chat_id: int,
    original_chat_id: int,
    file: str,
    title: str,
    duration: str,
    user: str,
    vidid: str,
    stream: str,
    forceplay: Union[bool, str] = None,
):
    dur = 0
    if "://" in vidid:
        try:
            dur = await asyncio.get_event_loop().run_in_executor(
                None, check_duration, vidid
            )
            duration = seconds_to_min(dur)
        except Exception:
            duration = "URL Stream"

    item = {
        "title": title,
        "dur": duration,
        "streamtype": stream,
        "by": user,
        "chat_id": original_chat_id,
        "file": file,
        "vidid": vidid,
        "seconds": int(dur),
        "played": 0,
    }

    if forceplay:
        existing = db.get(chat_id)
        if existing:
            existing.insert(0, item)
        else:
            db[chat_id] = [item]
    else:
        db.setdefault(chat_id, []).append(item)
