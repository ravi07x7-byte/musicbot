import os
from random import randint
from typing import Union

from pyrogram.types import InlineKeyboardMarkup

import config
from PriyaMusic import Carbon, YouTube, app
from PriyaMusic.core.call import Priya
from PriyaMusic.misc import db
from PriyaMusic.utils.database import add_active_video_chat, is_active_chat
from PriyaMusic.utils.exceptions import AssistantErr
from PriyaMusic.utils.inline import aq_markup, close_markup, stream_markup
from PriyaMusic.utils.pastebin import PriyaBin
from PriyaMusic.utils.stream.queue import put_queue, put_queue_index
from PriyaMusic.utils.thumbnails import get_thumb


async def stream(
    _,
    mystic,
    user_id,
    result,
    chat_id,
    user_name,
    original_chat_id,
    video: Union[bool, None] = None,
    streamtype: Union[str, None] = None,
    spotify: Union[bool, None] = None,
    forceplay: Union[bool, None] = None,
):
    if not result:
        return
    if forceplay:
        await Priya.force_stop_stream(chat_id)

    # ── Playlist ────────────────────────────────────────────
    if streamtype == "playlist":
        msg = f"{_['play_19']}\n\n"
        count = 0
        for search in result:
            if count >= config.PLAYLIST_FETCH_LIMIT:
                break
            try:
                title, dur_min, dur_sec, thumb, vidid = await YouTube.details(
                    search, False if spotify else True
                )
            except Exception:
                continue
            if dur_min is None or dur_sec > config.DURATION_LIMIT:
                continue
            status = True if video else None
            if await is_active_chat(chat_id):
                await put_queue(chat_id, original_chat_id, f"vid_{vidid}", title,
                                dur_min, user_name, vidid, user_id,
                                "video" if video else "audio")
                pos = len(db.get(chat_id, [])) - 1
                count += 1
                msg += f"{count}. {title[:70]}\n{_['play_20']} {pos}\n\n"
            else:
                db.setdefault(chat_id, [])
                try:
                    fp, direct = await YouTube.download(vidid, mystic, video=status, videoid=True)
                except Exception:
                    raise AssistantErr(_["play_14"])
                await Priya.join_call(chat_id, original_chat_id, fp, video=status, image=thumb)
                await put_queue(chat_id, original_chat_id, fp if direct else f"vid_{vidid}",
                                title, dur_min, user_name, vidid, user_id,
                                "video" if video else "audio", forceplay=forceplay)
                img = await get_thumb(vidid)
                btn = stream_markup(_, chat_id)
                run = await app.send_photo(
                    original_chat_id, photo=img,
                    caption=_["stream_1"].format(
                        f"https://t.me/{app.username}?start=info_{vidid}",
                        title[:23], dur_min, user_name),
                    reply_markup=InlineKeyboardMarkup(btn), has_spoiler=True)
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"
        if count == 0:
            return
        from PriyaMusic.utils.pastebin import PriyaBin
        link = await PriyaBin(msg)
        lines = msg.count("\n")
        car_text = os.linesep.join(msg.split(os.linesep)[:17]) if lines >= 17 else msg
        carbon = await Carbon.generate(car_text, randint(100, 9999999))
        return await app.send_photo(
            original_chat_id, photo=carbon,
            caption=_["play_21"].format(pos, link),
            reply_markup=close_markup(_), has_spoiler=True)

    # ── YouTube ─────────────────────────────────────────────
    elif streamtype == "youtube":
        vidid = result["vidid"]
        title = result["title"].title()
        dur_min = result["duration_min"]
        thumb = result["thumb"]
        status = True if video else None
        try:
            fp, direct = await YouTube.download(vidid, mystic, videoid=True, video=status)
        except Exception:
            raise AssistantErr(_["play_14"])
        if await is_active_chat(chat_id):
            await put_queue(chat_id, original_chat_id,
                            fp if direct else f"vid_{vidid}",
                            title, dur_min, user_name, vidid, user_id,
                            "video" if video else "audio")
            pos = len(db.get(chat_id, [])) - 1
            await app.send_message(original_chat_id,
                                   text=_["queue_4"].format(pos, title[:27], dur_min, user_name),
                                   reply_markup=InlineKeyboardMarkup(aq_markup(_, chat_id)))
        else:
            db.setdefault(chat_id, [])
            await Priya.join_call(chat_id, original_chat_id, fp, video=status, image=thumb)
            await put_queue(chat_id, original_chat_id, fp if direct else f"vid_{vidid}",
                            title, dur_min, user_name, vidid, user_id,
                            "video" if video else "audio", forceplay=forceplay)
            img = await get_thumb(vidid)
            btn = stream_markup(_, chat_id)
            run = await app.send_photo(
                original_chat_id, photo=img,
                caption=_["stream_1"].format(
                    f"https://t.me/{app.username}?start=info_{vidid}",
                    title[:23], dur_min, user_name),
                reply_markup=InlineKeyboardMarkup(btn), has_spoiler=True)
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "stream"

    # ── SoundCloud ──────────────────────────────────────────
    elif streamtype == "soundcloud":
        fp = result["filepath"]
        title = result["title"]
        dur_min = result["duration_min"]
        if await is_active_chat(chat_id):
            await put_queue(chat_id, original_chat_id, fp, title, dur_min,
                            user_name, "soundcloud", user_id, "audio")
            pos = len(db.get(chat_id, [])) - 1
            await app.send_message(original_chat_id,
                                   text=_["queue_4"].format(pos, title[:27], dur_min, user_name),
                                   reply_markup=InlineKeyboardMarkup(aq_markup(_, chat_id)))
        else:
            db.setdefault(chat_id, [])
            await Priya.join_call(chat_id, original_chat_id, fp)
            await put_queue(chat_id, original_chat_id, fp, title, dur_min,
                            user_name, "soundcloud", user_id, "audio", forceplay=forceplay)
            btn = stream_markup(_, chat_id)
            run = await app.send_photo(
                original_chat_id, photo=config.SOUNDCLOUD_IMG_URL,
                caption=_["stream_1"].format(config.SUPPORT_CHAT, title[:23], dur_min, user_name),
                reply_markup=InlineKeyboardMarkup(btn), has_spoiler=True)
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"

    # ── Telegram ────────────────────────────────────────────
    elif streamtype == "telegram":
        fp = result["path"]
        link = result["link"]
        title = result["title"].title()
        dur_min = result["dur"]
        status = True if video else None
        if await is_active_chat(chat_id):
            await put_queue(chat_id, original_chat_id, fp, title, dur_min,
                            user_name, "telegram", user_id,
                            "video" if video else "audio")
            pos = len(db.get(chat_id, [])) - 1
            await app.send_message(original_chat_id,
                                   text=_["queue_4"].format(pos, title[:27], dur_min, user_name),
                                   reply_markup=InlineKeyboardMarkup(aq_markup(_, chat_id)))
        else:
            db.setdefault(chat_id, [])
            await Priya.join_call(chat_id, original_chat_id, fp, video=status)
            await put_queue(chat_id, original_chat_id, fp, title, dur_min,
                            user_name, "telegram", user_id,
                            "video" if video else "audio", forceplay=forceplay)
            if video:
                await add_active_video_chat(chat_id)
            photo = config.TELEGRAM_VIDEO_URL if video else config.TELEGRAM_AUDIO_URL
            btn = stream_markup(_, chat_id)
            run = await app.send_photo(
                original_chat_id, photo=photo,
                caption=_["stream_1"].format(link, title[:23], dur_min, user_name),
                reply_markup=InlineKeyboardMarkup(btn), has_spoiler=True)
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"

    # ── Live ────────────────────────────────────────────────
    elif streamtype == "live":
        vidid = result["vidid"]
        title = result["title"].title()
        thumb = result["thumb"]
        dur_min = "Live"
        status = True if video else None
        if await is_active_chat(chat_id):
            await put_queue(chat_id, original_chat_id, f"live_{vidid}", title,
                            dur_min, user_name, vidid, user_id,
                            "video" if video else "audio")
            pos = len(db.get(chat_id, [])) - 1
            await app.send_message(original_chat_id,
                                   text=_["queue_4"].format(pos, title[:27], dur_min, user_name),
                                   reply_markup=InlineKeyboardMarkup(aq_markup(_, chat_id)))
        else:
            db.setdefault(chat_id, [])
            n, fp = await YouTube.video(result["link"])
            if n == 0:
                raise AssistantErr(_["str_3"])
            await Priya.join_call(chat_id, original_chat_id, fp, video=status, image=thumb)
            await put_queue(chat_id, original_chat_id, f"live_{vidid}", title, dur_min,
                            user_name, vidid, user_id,
                            "video" if video else "audio", forceplay=forceplay)
            img = await get_thumb(vidid)
            btn = stream_markup(_, chat_id)
            run = await app.send_photo(
                original_chat_id, photo=img,
                caption=_["stream_1"].format(
                    f"https://t.me/{app.username}?start=info_{vidid}",
                    title[:23], dur_min, user_name),
                reply_markup=InlineKeyboardMarkup(btn), has_spoiler=True)
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"

    # ── Index / M3U8 ────────────────────────────────────────
    elif streamtype == "index":
        link = result
        title = "Index / M3U8 Stream"
        dur_min = "00:00"
        if await is_active_chat(chat_id):
            await put_queue_index(chat_id, original_chat_id, "index_url", title,
                                  dur_min, user_name, link,
                                  "video" if video else "audio")
            pos = len(db.get(chat_id, [])) - 1
            if mystic:
                await mystic.edit_text(
                    text=_["queue_4"].format(pos, title[:27], dur_min, user_name),
                    reply_markup=InlineKeyboardMarkup(aq_markup(_, chat_id)))
        else:
            db.setdefault(chat_id, [])
            await Priya.join_call(chat_id, original_chat_id, link, video=True if video else None)
            await put_queue_index(chat_id, original_chat_id, "index_url", title,
                                  dur_min, user_name, link,
                                  "video" if video else "audio", forceplay=forceplay)
            btn = stream_markup(_, chat_id)
            run = await app.send_photo(
                original_chat_id, photo=config.STREAM_IMG_URL,
                caption=_["stream_2"].format(user_name),
                reply_markup=InlineKeyboardMarkup(btn), has_spoiler=True)
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
            if mystic:
                await mystic.delete()
