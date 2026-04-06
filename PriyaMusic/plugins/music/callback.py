import asyncio

from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup

from PriyaMusic import YouTube, app
from PriyaMusic.core.call import Priya
from PriyaMusic.misc import SUDOERS, db
from PriyaMusic.utils.database import (
    get_lang,
    is_active_chat,
    is_music_playing,
    is_nonadmin_chat,
    music_off,
    music_on,
    set_loop,
)
from PriyaMusic.utils.decorators import ActualAdminCB, languageCB
from PriyaMusic.utils.formatters import seconds_to_min
from PriyaMusic.utils.inline import close_markup, stream_markup, stream_markup_timer
from PriyaMusic.utils.stream.autoclear import auto_clean
from PriyaMusic.utils.thumbnails import get_thumb
from config import BANNED_USERS, adminlist
from strings import get_string

import config


@app.on_callback_query(filters.regex(r"^ADMIN (.+)\|(-?\d+)$") & ~BANNED_USERS)
@languageCB
async def admin_cb(client, cq: CallbackQuery, _):
    data = cq.data.strip()
    parts = data.split(None, 1)[1]
    action, chat_id_str = parts.split("|")
    chat_id = int(chat_id_str)

    if not await is_active_chat(chat_id):
        return await cq.answer(_["general_5"], show_alert=True)

    # Permission check
    if not await is_nonadmin_chat(cq.message.chat.id):
        if cq.from_user.id not in SUDOERS:
            admins = adminlist.get(cq.message.chat.id, [])
            if cq.from_user.id not in admins:
                return await cq.answer(_["admin_14"], show_alert=True)

    if action == "Pause":
        if not await is_music_playing(chat_id):
            return await cq.answer(_["admin_1"], show_alert=True)
        await music_off(chat_id)
        await Priya.pause_stream(chat_id)
        await cq.answer("⏸ Paused")

    elif action == "Resume":
        if await is_music_playing(chat_id):
            return await cq.answer(_["admin_3"], show_alert=True)
        await music_on(chat_id)
        await Priya.resume_stream(chat_id)
        await cq.answer("▶️ Resumed")

    elif action == "Stop":
        await Priya.stop_stream(chat_id)
        await set_loop(chat_id, 0)
        await cq.answer("⏹ Stopped")
        try:
            await cq.message.delete()
        except Exception:
            pass

    elif action == "Skip":
        check = db.get(chat_id, [])
        if not check:
            return await cq.answer(_["queue_2"], show_alert=True)
        popped = check.pop(0) if check else None
        if popped:
            await auto_clean(popped)
        if not check:
            await cq.answer("✅ Queue ended")
            try:
                await Priya.stop_stream(chat_id)
                await cq.message.delete()
            except Exception:
                pass
            return
        nxt = check[0]
        nxt["played"] = 0
        file = nxt["file"]
        vidid = nxt["vidid"]
        title = nxt["title"].title()
        user = nxt["by"]
        status = nxt["streamtype"] == "video"
        try:
            if "vid_" in file:
                n, fp = await YouTube.video(vidid, True)
                if n == 0:
                    return await cq.answer("Failed to load next track.", show_alert=True)
                file = fp
            await Priya.skip_stream(chat_id, file, video=status)
            await cq.answer("⏭ Skipped")
            img = await get_thumb(vidid) if vidid not in ("telegram", "soundcloud") else config.YOUTUBE_IMG_URL
            btn = stream_markup(_, chat_id)
            run = await cq.message.reply_photo(
                photo=img,
                caption=_["stream_1"].format(
                    f"https://t.me/{app.username}?start=info_{vidid}",
                    title[:23], nxt["dur"], user,
                ),
                reply_markup=InlineKeyboardMarkup(btn),
            )
            db[chat_id][0]["mystic"] = run
            try:
                await cq.message.delete()
            except Exception:
                pass
        except Exception:
            await cq.answer("Error skipping.", show_alert=True)

    elif action == "Replay":
        check = db.get(chat_id, [])
        if not check:
            return await cq.answer(_["queue_2"], show_alert=True)
        check[0]["played"] = 0
        file = check[0]["file"]
        status = check[0]["streamtype"] == "video"
        try:
            if "vid_" in file:
                n, fp = await YouTube.video(check[0]["vidid"], True)
                if n == 0:
                    return await cq.answer("Failed to replay.", show_alert=True)
                file = fp
            await Priya.skip_stream(chat_id, file, video=status)
            await cq.answer("↻ Replaying")
        except Exception:
            await cq.answer("Error replaying.", show_alert=True)

    elif action == "UpVote":
        from config import confirmer
        # Voting skip logic
        pass


@app.on_callback_query(filters.regex("^SpeedUP ") & ~BANNED_USERS)
@languageCB
async def speed_cb(client, cq: CallbackQuery, _):
    parts = cq.data.split(None, 1)[1].split("|")
    chat_id, speed = int(parts[0]), parts[1]

    if not await is_active_chat(chat_id):
        return await cq.answer(_["general_5"], show_alert=True)

    if not await is_nonadmin_chat(cq.message.chat.id):
        if cq.from_user.id not in SUDOERS:
            admins = adminlist.get(cq.message.chat.id, [])
            if cq.from_user.id not in admins:
                return await cq.answer(_["admin_14"], show_alert=True)

    playing = db.get(chat_id)
    if not playing:
        return await cq.answer(_["queue_2"], show_alert=True)
    if int(playing[0]["seconds"]) == 0:
        return await cq.answer(_["admin_27"], show_alert=True)
    file = playing[0]["file"]
    if "downloads" not in file:
        return await cq.answer(_["admin_27"], show_alert=True)

    cur_speed = playing[0].get("speed", 1.0)
    if str(cur_speed) == speed:
        if speed == "1.0":
            return await cq.answer(_["admin_29"], show_alert=True)

    mystic = await cq.edit_message_text(
        _["admin_32"].format(cq.from_user.mention)
    )
    try:
        await Priya.speedup_stream(chat_id, file, speed, playing)
    except Exception:
        return await mystic.edit_text(_["admin_33"], reply_markup=close_markup(_))
    await mystic.edit_text(
        _["admin_34"].format(speed, cq.from_user.mention),
        reply_markup=close_markup(_),
    )


@app.on_callback_query(filters.regex("^MusicStream ") & ~BANNED_USERS)
@languageCB
async def music_stream_cb(client, cq: CallbackQuery, _):
    data = cq.data.split(None, 1)[1]
    parts = data.split("|")
    if len(parts) < 5:
        return
    vidid, user_id, mode, cplay, fplay = parts
    if cq.from_user.id != int(user_id):
        return await cq.answer(_["playcb_1"], show_alert=True)

    from PriyaMusic.utils.channelplay import get_channeplayCB
    try:
        chat_id, channel = await get_channeplayCB(_, cplay, cq)
    except Exception:
        return

    video = True if mode == "v" else None
    user_name = cq.from_user.first_name
    forceplay = True if fplay == "f" else None

    await cq.message.delete()
    try:
        await cq.answer()
    except Exception:
        pass
    mystic = await cq.message.reply_text(
        _["play_2"].format(channel) if channel else _["play_1"]
    )
    try:
        details, track_id = await YouTube.track(vidid, True)
    except Exception:
        return await mystic.edit_text(_["play_3"])

    from PriyaMusic.utils.stream.stream import stream
    try:
        await stream(_, mystic, int(user_id), details, chat_id, user_name,
                     cq.message.chat.id, video=video, streamtype="youtube", forceplay=forceplay)
    except Exception as e:
        err = str(e) if "AssistantErr" in type(e).__name__ else _["general_2"].format(type(e).__name__)
        await mystic.edit_text(err)
    try:
        await mystic.delete()
    except Exception:
        pass


@app.on_callback_query(filters.regex("^GetTimer$") & ~BANNED_USERS)
async def get_timer_cb(client, cq: CallbackQuery):
    await cq.answer()


@app.on_callback_query(filters.regex("^PriyaAdmin$"))
async def priya_admin_cb(client, cq: CallbackQuery):
    await cq.answer(
        "To use anonymous admin commands: Go to Group Settings → Administrators "
        "→ Uncheck 'Remain Anonymous' for your account.",
        show_alert=True,
    )
