import random

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, Message

import config
from PriyaMusic import YouTube, app
from PriyaMusic.core.call import Priya
from PriyaMusic.misc import SUDOERS, db
from PriyaMusic.utils.database import (
    get_loop,
    is_active_chat,
    is_music_playing,
    is_nonadmin_chat,
    music_off,
    music_on,
    set_loop,
)
from PriyaMusic.utils.decorators import AdminRightsCheck, language
from PriyaMusic.utils.formatters import seconds_to_min
from PriyaMusic.utils.inline import close_markup, speed_markup, stream_markup
from PriyaMusic.utils.stream.autoclear import auto_clean
from PriyaMusic.utils.thumbnails import get_thumb
from config import BANNED_USERS, adminlist


# ─── Pause ──────────────────────────────────────────────────
@app.on_message(filters.command(["pause", "cpause"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def pause_cmd(cli, message: Message, _, chat_id):
    if not await is_music_playing(chat_id):
        return await message.reply_text(_["admin_1"])
    await music_off(chat_id)
    await Priya.pause_stream(chat_id)
    await message.reply_text(
        _["admin_2"].format(message.from_user.mention),
        reply_markup=close_markup(_),
    )


# ─── Resume ─────────────────────────────────────────────────
@app.on_message(filters.command(["resume", "cresume"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def resume_cmd(cli, message: Message, _, chat_id):
    if await is_music_playing(chat_id):
        return await message.reply_text(_["admin_3"])
    await music_on(chat_id)
    await Priya.resume_stream(chat_id)
    await message.reply_text(
        _["admin_4"].format(message.from_user.mention),
        reply_markup=close_markup(_),
    )


# ─── Stop ───────────────────────────────────────────────────
@app.on_message(filters.command(["end", "stop", "cend", "cstop"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def stop_cmd(cli, message: Message, _, chat_id):
    if len(message.command) != 1:
        return
    await Priya.stop_stream(chat_id)
    await set_loop(chat_id, 0)
    await message.reply_text(
        _["admin_5"].format(message.from_user.mention),
        reply_markup=close_markup(_),
    )


# ─── Skip ───────────────────────────────────────────────────
@app.on_message(filters.command(["skip", "cskip", "next", "cnext"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def skip_cmd(cli, message: Message, _, chat_id):
    check = db.get(chat_id)
    if not check:
        return await message.reply_text(_["queue_2"])

    # Skip N tracks
    if len(message.command) >= 2:
        loop = await get_loop(chat_id)
        if loop:
            return await message.reply_text(_["admin_8"])
        arg = message.command[1]
        if not arg.isnumeric():
            return await message.reply_text(_["admin_9"])
        n = int(arg)
        total = len(check) - 1
        if total < 1:
            return await message.reply_text(_["admin_10"])
        if n > total:
            return await message.reply_text(_["admin_11"].format(total))
        for _ in range(n):
            popped = check.pop(0) if check else None
            if popped:
                await auto_clean(popped)
            if not check:
                await message.reply_text(
                    _["admin_6"].format(message.from_user.mention, message.chat.title),
                    reply_markup=close_markup(_),
                )
                try:
                    await Priya.stop_stream(chat_id)
                except Exception:
                    pass
                return
    else:
        popped = check.pop(0) if check else None
        if popped:
            await auto_clean(popped)
        if not check:
            await message.reply_text(
                _["admin_6"].format(message.from_user.mention, message.chat.title),
                reply_markup=close_markup(_),
            )
            try:
                await Priya.stop_stream(chat_id)
            except Exception:
                pass
            return

    nxt = check[0]
    nxt["played"] = 0
    file = nxt["file"]
    vidid = nxt["vidid"]
    title = nxt["title"].title()
    user = nxt["by"]
    streamtype = nxt["streamtype"]
    status = streamtype == "video"

    # Handle old speed state
    if nxt.get("old_dur"):
        db[chat_id][0]["dur"] = nxt["old_dur"]
        db[chat_id][0]["seconds"] = nxt["old_second"]
        db[chat_id][0]["speed_path"] = None
        db[chat_id][0]["speed"] = 1.0

    try:
        if "live_" in file:
            n, link = await YouTube.video(vidid, True)
            if n == 0:
                return await message.reply_text(_["admin_7"].format(title))
            await Priya.skip_stream(chat_id, link, video=status)
        elif "vid_" in file:
            mystic = await message.reply_text("⏳ Loading next track...")
            fp, direct = await YouTube.download(vidid, mystic, videoid=True, video=status)
            await Priya.skip_stream(chat_id, fp, video=status)
            await mystic.delete()
        elif "index_" in file:
            await Priya.skip_stream(chat_id, vidid, video=status)
        else:
            await Priya.skip_stream(chat_id, file, video=status)

        img = await get_thumb(vidid) if vidid not in ("telegram", "soundcloud") else config.YOUTUBE_IMG_URL
        btn = stream_markup(_, chat_id)
        run = await message.reply_photo(
            photo=img,
            caption=_["stream_1"].format(
                f"https://t.me/{app.username}?start=info_{vidid}",
                title[:23], nxt["dur"], user,
            ),
            reply_markup=InlineKeyboardMarkup(btn),
        )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "stream"
    except Exception:
        await message.reply_text(_["call_6"] if hasattr(_, '__getitem__') else "Error skipping track.")


# ─── Loop ───────────────────────────────────────────────────
@app.on_message(filters.command(["loop", "cloop"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def loop_cmd(cli, message: Message, _, chat_id):
    if len(message.command) != 2:
        return await message.reply_text(_["admin_17"])
    arg = message.command[1].strip().lower()
    if arg.isnumeric():
        n = int(arg)
        if not 1 <= n <= 10:
            return await message.reply_text(_["admin_17"])
        current = await get_loop(chat_id)
        new = min(current + n, 10)
        await set_loop(chat_id, new)
        return await message.reply_text(
            _["admin_18"].format(new, message.from_user.mention),
            reply_markup=close_markup(_),
        )
    if arg == "enable":
        await set_loop(chat_id, 10)
        return await message.reply_text(
            _["admin_18"].format(10, message.from_user.mention),
            reply_markup=close_markup(_),
        )
    if arg == "disable":
        await set_loop(chat_id, 0)
        return await message.reply_text(
            _["admin_19"].format(message.from_user.mention),
            reply_markup=close_markup(_),
        )
    await message.reply_text(_["admin_17"])


# ─── Shuffle ────────────────────────────────────────────────
@app.on_message(filters.command(["shuffle", "cshuffle"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def shuffle_cmd(cli, message: Message, _, chat_id):
    check = db.get(chat_id)
    if not check:
        return await message.reply_text(_["queue_2"])
    if len(check) <= 1:
        return await message.reply_text(_["admin_15"], reply_markup=close_markup(_))
    first = check.pop(0)
    random.shuffle(check)
    check.insert(0, first)
    await message.reply_text(
        _["admin_16"].format(message.from_user.mention),
        reply_markup=close_markup(_),
    )


# ─── Seek ───────────────────────────────────────────────────
@app.on_message(
    filters.command(["seek", "cseek", "seekback", "cseekback"]) & filters.group & ~BANNED_USERS
)
@AdminRightsCheck
async def seek_cmd(cli, message: Message, _, chat_id):
    if len(message.command) < 2:
        return await message.reply_text(_["admin_20"])
    arg = message.command[1].strip()
    if not arg.isnumeric():
        return await message.reply_text(_["admin_21"])
    playing = db.get(chat_id)
    if not playing:
        return await message.reply_text(_["queue_2"])
    dur_sec = int(playing[0]["seconds"])
    if dur_sec == 0:
        return await message.reply_text(_["admin_22"])

    played = int(playing[0]["played"])
    skip = int(arg)
    dur = playing[0]["dur"]
    cmd = message.command[0]
    seeking_back = cmd.endswith("back")

    if seeking_back:
        if played - skip <= 10:
            return await message.reply_text(
                _["admin_23"].format(seconds_to_min(played), dur),
                reply_markup=close_markup(_),
            )
        to_seek = played - skip + 1
    else:
        if dur_sec - (played + skip) <= 10:
            return await message.reply_text(
                _["admin_23"].format(seconds_to_min(played), dur),
                reply_markup=close_markup(_),
            )
        to_seek = played + skip + 1

    mystic = await message.reply_text(_["admin_24"])
    file = playing[0]["file"]
    if "vid_" in file:
        n, file = await YouTube.video(playing[0]["vidid"], True)
        if n == 0:
            return await mystic.edit_text(_["admin_22"])
    check_speed = playing[0].get("speed_path")
    if check_speed:
        file = check_speed
    if "index_" in file:
        file = playing[0]["vidid"]

    try:
        await Priya.seek_stream(
            chat_id, file,
            seconds_to_min(to_seek),
            dur,
            playing[0]["streamtype"],
        )
    except Exception:
        return await mystic.edit_text(_["admin_26"], reply_markup=close_markup(_))

    if seeking_back:
        db[chat_id][0]["played"] -= skip
    else:
        db[chat_id][0]["played"] += skip

    await mystic.edit_text(
        _["admin_25"].format(seconds_to_min(to_seek), message.from_user.mention),
        reply_markup=close_markup(_),
    )


# ─── Speed ──────────────────────────────────────────────────
@app.on_message(
    filters.command(["speed", "cspeed", "slow", "cslow", "playback", "cplayback"])
    & filters.group
    & ~BANNED_USERS
)
@AdminRightsCheck
async def speed_cmd(cli, message: Message, _, chat_id):
    playing = db.get(chat_id)
    if not playing:
        return await message.reply_text(_["queue_2"])
    if int(playing[0]["seconds"]) == 0:
        return await message.reply_text(_["admin_27"])
    if "downloads" not in playing[0]["file"]:
        return await message.reply_text(_["admin_27"])
    await message.reply_text(
        _["admin_28"].format(app.mention),
        reply_markup=speed_markup(_, chat_id),
    )
