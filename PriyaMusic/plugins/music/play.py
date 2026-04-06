from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, Message

import config
from PriyaMusic import Apple, Resso, SoundCloud, Spotify, Telegram, YouTube, app
from PriyaMusic.misc import SUDOERS
from PriyaMusic.utils.database import (
    add_served_chat,
    get_cmode,
    get_lang,
    get_playmode,
    get_playtype,
    is_active_chat,
    is_maintenance,
)
from PriyaMusic.utils.decorators.play import PlayWrapper
from PriyaMusic.utils.inline import slider_markup, track_markup
from PriyaMusic.utils.logger import play_logs
from PriyaMusic.utils.stream.stream import stream
from config import BANNED_USERS, adminlist
from strings import get_string


@app.on_message(
    filters.command(
        ["play", "vplay", "cplay", "cvplay",
         "playforce", "vplayforce", "cplayforce", "cvplayforce"]
    )
    & filters.group
    & ~BANNED_USERS
)
@PlayWrapper
async def play_command(
    client,
    message: Message,
    _,
    chat_id,
    video,
    channel,
    playmode,
    url,
    fplay,
):
    await add_served_chat(message.chat.id)
    await play_logs(message, "Video" if video else "Audio")

    mystic = await message.reply_text(
        _["play_2"].format(channel) if channel else _["play_1"]
    )

    # ── Telegram audio/video reply ───────────────────────
    reply = message.reply_to_message
    if reply:
        audio = reply.audio or reply.voice
        video_file = reply.video or reply.document
        if audio:
            fname = await Telegram.get_filename(audio, audio=True)
            fpath = await Telegram.get_filepath(audio=audio)
            dur = await Telegram.get_duration(audio, fpath)
            link = reply.link
            from config import lyrical
            lyrical[mystic.id] = True
            downloaded = await Telegram.download(_, message, mystic, fpath)
            if not downloaded:
                return
            await stream(
                _, mystic, message.from_user.id,
                {"title": fname, "dur": dur, "path": fpath, "link": link},
                chat_id, message.from_user.mention, message.chat.id,
                video=None, streamtype="telegram", forceplay=fplay,
            )
            return
        if video_file and video:
            fname = await Telegram.get_filename(video_file)
            fpath = await Telegram.get_filepath(video=video_file)
            dur = await Telegram.get_duration(video_file, fpath)
            link = reply.link
            from config import lyrical
            lyrical[mystic.id] = True
            downloaded = await Telegram.download(_, message, mystic, fpath)
            if not downloaded:
                return
            await stream(
                _, mystic, message.from_user.id,
                {"title": fname, "dur": dur, "path": fpath, "link": link},
                chat_id, message.from_user.mention, message.chat.id,
                video=True, streamtype="telegram", forceplay=fplay,
            )
            return

    # ── URL-based play ───────────────────────────────────
    query = None
    if url:
        query = url
    elif len(message.command) > 1:
        query = message.text.split(None, 1)[1].strip()

    if not query:
        return await mystic.edit_text(_["play_18"])

    # Spotify
    if await Spotify.valid(query):
        if "track" in query:
            details, vidid = await Spotify.track(query)
            if not details:
                return await mystic.edit_text(_["play_3"])
            await stream(
                _, mystic, message.from_user.id, details, chat_id,
                message.from_user.mention, message.chat.id,
                video=video, streamtype="youtube", forceplay=fplay,
            )
        elif "playlist" in query:
            result, pid = await Spotify.playlist(query)
            if not result:
                return await mystic.edit_text(_["play_3"])
            await stream(
                _, mystic, message.from_user.id, result, chat_id,
                message.from_user.mention, message.chat.id,
                video=video, streamtype="playlist", spotify=True, forceplay=fplay,
            )
        elif "album" in query:
            result, aid = await Spotify.album(query)
            if not result:
                return await mystic.edit_text(_["play_3"])
            await stream(
                _, mystic, message.from_user.id, result, chat_id,
                message.from_user.mention, message.chat.id,
                video=video, streamtype="playlist", spotify=True, forceplay=fplay,
            )
        elif "artist" in query:
            result, aid = await Spotify.artist(query)
            if not result:
                return await mystic.edit_text(_["play_3"])
            await stream(
                _, mystic, message.from_user.id, result, chat_id,
                message.from_user.mention, message.chat.id,
                video=video, streamtype="playlist", spotify=True, forceplay=fplay,
            )
        return

    # SoundCloud
    if await SoundCloud.valid(query):
        result, fpath = await SoundCloud.download(query)
        if not result:
            return await mystic.edit_text(_["play_3"])
        await stream(
            _, mystic, message.from_user.id, result, chat_id,
            message.from_user.mention, message.chat.id,
            video=None, streamtype="soundcloud", forceplay=fplay,
        )
        return

    # Apple Music
    if await Apple.valid(query):
        details, vidid = await Apple.track(query)
        if not details:
            return await mystic.edit_text(_["play_3"])
        await stream(
            _, mystic, message.from_user.id, details, chat_id,
            message.from_user.mention, message.chat.id,
            video=video, streamtype="youtube", forceplay=fplay,
        )
        return

    # Resso
    if await Resso.valid(query):
        details, vidid = await Resso.track(query)
        if not details:
            return await mystic.edit_text(_["play_3"])
        await stream(
            _, mystic, message.from_user.id, details, chat_id,
            message.from_user.mention, message.chat.id,
            video=video, streamtype="youtube", forceplay=fplay,
        )
        return

    # YouTube URL
    if await YouTube.exists(query):
        if "playlist" in query:
            result = await YouTube.playlist(query, config.PLAYLIST_FETCH_LIMIT, message.from_user.id)
            if not result:
                return await mystic.edit_text(_["play_3"])
            await stream(
                _, mystic, message.from_user.id, result, chat_id,
                message.from_user.mention, message.chat.id,
                video=video, streamtype="playlist", forceplay=fplay,
            )
            return
        details, vidid = await YouTube.track(query)
        if not details:
            return await mystic.edit_text(_["play_3"])
        if not details.get("duration_min"):
            # Live stream
            await stream(
                _, mystic, message.from_user.id, details, chat_id,
                message.from_user.mention, message.chat.id,
                video=video, streamtype="live", forceplay=fplay,
            )
        else:
            await stream(
                _, mystic, message.from_user.id, details, chat_id,
                message.from_user.mention, message.chat.id,
                video=video, streamtype="youtube", forceplay=fplay,
            )
        return

    # Search query
    if playmode == "Direct":
        details, vidid = await YouTube.track(query)
        if not details:
            return await mystic.edit_text(_["play_3"])
        await stream(
            _, mystic, message.from_user.id, details, chat_id,
            message.from_user.mention, message.chat.id,
            video=video, streamtype="youtube", forceplay=fplay,
        )
    else:
        # Interactive search — show slider
        try:
            result = await YouTube.slider(query, 0)
            if not result:
                return await mystic.edit_text(_["play_3"])
            title, dur, thumb, vidid = result
            btn = slider_markup(
                _, vidid, message.from_user.id, query, 0,
                "c" if channel else "g", "f" if fplay else "n",
            )
            await mystic.edit_text(
                f"🔍 <b>{title}</b>\n⏱ {dur}",
                reply_markup=InlineKeyboardMarkup(btn),
            )
        except Exception:
            return await mystic.edit_text(_["play_3"])

    await mystic.delete()
