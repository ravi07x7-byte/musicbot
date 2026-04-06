"""
PriyaMusic — Voice/Video call engine.
Wraps PyTgCalls for all stream operations.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Union

from pytgcalls import PyTgCalls

# PyTgCalls changed exception exports across versions. Import defensively.
try:
    from pytgcalls.exceptions import (
        AlreadyJoinedError,
        NoActiveGroupCall,
        NotInCallError,
    )
except Exception:
    class AlreadyJoinedError(Exception):
        pass

    class NoActiveGroupCall(Exception):
        pass

    class NotInCallError(Exception):
        pass
# Import types from pytgcalls; handle re-organization across versions.
try:
    from pytgcalls.types import (
        AudioPiped,
        AudioVideoPiped,
        MediaStream,
        VideoPiped,
    )
except Exception:
    # Try alternate submodules
    try:
        from pytgcalls.types.stream import MediaStream
    except Exception:
        MediaStream = None

    try:
        from pytgcalls.types.pipes import AudioPiped, AudioVideoPiped, VideoPiped
    except Exception:
        AudioPiped = AudioVideoPiped = VideoPiped = None

    # Provide a minimal fallback MediaStream with Flags used by the code.
    if MediaStream is None:
        class _Flags:
            IGNORE = 0

        class MediaStream:
            Flags = _Flags

            def __init__(self, file, **kwargs):
                self.file = file
                self.kwargs = kwargs

from pytgcalls.types.input_stream import AudioParameters, VideoParameters

import config
from PriyaMusic.core.mongo import mongodb
from PriyaMusic.utils.database import (
    add_active_chat,
    get_active_chats,
    is_autoend,
    music_off,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from .logging import LOGGER

# Autoend tracker: {chat_id: datetime}
autoend: dict[int, datetime] = {}

# Speed state: {chat_id: float}
_speed: dict[int, float] = {}


class _PriyaCall:
    def __init__(self):
        self._calls: dict[int, PyTgCalls] = {}  # assistant_num -> PyTgCalls
        self._chat_assistant: dict[int, int] = {}  # chat_id -> assistant_num

    def register(self, num: int, client):
        call = PyTgCalls(client)
        self._calls[num] = call
        return call

    def _get_call(self, chat_id: int) -> PyTgCalls:
        num = self._chat_assistant.get(chat_id, 1)
        return self._calls.get(num, list(self._calls.values())[0])

    # ── Stream control ──────────────────────────────────────

    async def join_call(
        self,
        chat_id: int,
        original_chat_id: int,
        file: str,
        video: Union[bool, None] = None,
        image: Union[str, None] = None,
    ):
        call = self._get_call(chat_id)
        try:
            if video:
                stream = MediaStream(
                    file,
                    audio_parameters=AudioParameters.from_quality("high"),
                    video_parameters=VideoParameters.from_quality("sd_480p"),
                )
            else:
                stream = MediaStream(
                    file,
                    audio_parameters=AudioParameters.from_quality("high"),
                    video_flags=MediaStream.Flags.IGNORE,
                )
            await call.join_group_call(chat_id, stream)
        except AlreadyJoinedError:
            await call.change_stream(chat_id, stream if video else MediaStream(
                file,
                audio_parameters=AudioParameters.from_quality("high"),
                video_flags=MediaStream.Flags.IGNORE,
            ))
        except NoActiveGroupCall:
            raise
        await add_active_chat(chat_id)
        await music_on(chat_id)
        autoend[chat_id] = datetime.now() + timedelta(minutes=config.AUTOPLAY_IDLE_MINUTES)

    async def pause_stream(self, chat_id: int):
        call = self._get_call(chat_id)
        await call.pause_stream(chat_id)

    async def resume_stream(self, chat_id: int):
        call = self._get_call(chat_id)
        await call.resume_stream(chat_id)

    async def stop_stream(self, chat_id: int):
        call = self._get_call(chat_id)
        try:
            await call.leave_group_call(chat_id)
        except Exception:
            pass
        await remove_active_chat(chat_id)
        await remove_active_video_chat(chat_id)
        await music_off(chat_id)
        await set_loop(chat_id, 0)
        autoend.pop(chat_id, None)

    async def stop_stream_force(self, chat_id: int):
        from PriyaMusic.misc import db
        db.pop(chat_id, None)
        await self.stop_stream(chat_id)

    async def force_stop_stream(self, chat_id: int):
        await self.stop_stream_force(chat_id)

    async def skip_stream(
        self,
        chat_id: int,
        file: str,
        video: Union[bool, None] = None,
        image: Union[str, None] = None,
    ):
        call = self._get_call(chat_id)
        if video:
            stream = MediaStream(
                file,
                audio_parameters=AudioParameters.from_quality("high"),
                video_parameters=VideoParameters.from_quality("sd_480p"),
            )
        else:
            stream = MediaStream(
                file,
                audio_parameters=AudioParameters.from_quality("high"),
                video_flags=MediaStream.Flags.IGNORE,
            )
        await call.change_stream(chat_id, stream)
        await music_on(chat_id)

    async def seek_stream(self, chat_id: int, file: str, to_seek: str, duration: str, streamtype: str):
        call = self._get_call(chat_id)
        video = streamtype == "video"
        if video:
            stream = MediaStream(
                file,
                audio_parameters=AudioParameters.from_quality("high"),
                video_parameters=VideoParameters.from_quality("sd_480p"),
                ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
        else:
            stream = MediaStream(
                file,
                audio_parameters=AudioParameters.from_quality("high"),
                video_flags=MediaStream.Flags.IGNORE,
                ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
        await call.change_stream(chat_id, stream)

    async def speedup_stream(self, chat_id: int, file: str, speed: str, playing: list):
        from PriyaMusic.utils.formatters import seconds_to_min, speed_converter
        call = self._get_call(chat_id)
        duration_played = int(playing[0].get("played", 0))
        duration_seconds = int(playing[0].get("seconds", 0))
        spd = float(speed)
        to_seek, new_dur = speed_converter(duration_played, spd)
        _, full_dur = speed_converter(duration_seconds, spd)

        from PriyaMusic.misc import db
        db[chat_id][0]["speed"] = spd
        db[chat_id][0]["played"] = int(to_seek) if isinstance(to_seek, float) else duration_played

        if "old_dur" not in playing[0]:
            db[chat_id][0]["old_dur"] = playing[0]["dur"]
            db[chat_id][0]["old_second"] = playing[0]["seconds"]

        db[chat_id][0]["dur"] = seconds_to_min(int(full_dur))
        db[chat_id][0]["seconds"] = int(full_dur)

        new_file = f"downloads/{chat_id}_speed.mp3"
        import subprocess
        subprocess.Popen(
            ["ffmpeg", "-y", "-i", file, "-filter:a", f"atempo={spd}", "-vn", new_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).wait()

        db[chat_id][0]["speed_path"] = new_file
        stream = MediaStream(
            new_file,
            audio_parameters=AudioParameters.from_quality("high"),
            video_flags=MediaStream.Flags.IGNORE,
            ffmpeg_parameters=f"-ss {to_seek}",
        )
        await call.change_stream(chat_id, stream)

    async def stream_call(self, link: str):
        call = list(self._calls.values())[0]
        await call.join_group_call(
            config.LOGGER_ID,
            MediaStream(link, video_flags=MediaStream.Flags.IGNORE),
        )

    async def ping(self) -> str:
        return "pong"

    async def decorators(self):
        for num, call in self._calls.items():
            @call.on_stream_end()
            async def stream_ended(_, chat_id: int):
                await _on_stream_end(chat_id)

            @call.on_kicked()
            async def kicked(_, chat_id: int):
                await self.stop_stream_force(chat_id)

            @call.on_closed_voice_chat()
            async def closed(_, chat_id: int):
                await self.stop_stream_force(chat_id)

    async def start(self):
        for num, call in self._calls.items():
            await call.start()
            LOGGER(__name__).info(f"PyTgCalls started for assistant {num}")


async def _on_stream_end(chat_id: int):
    from PriyaMusic.misc import db
    from PriyaMusic.utils.database import get_loop
    from PriyaMusic import app
    import config

    playing = db.get(chat_id)
    if not playing:
        await Priya.stop_stream(chat_id)
        return

    loop = await get_loop(chat_id)
    if loop > 0:
        # replay same track
        await set_loop(chat_id, loop - 1)
        file = playing[0]["file"]
        video = playing[0]["streamtype"] == "video"
        try:
            await Priya.skip_stream(chat_id, file, video=video)
        except Exception:
            await Priya.stop_stream(chat_id)
        return

    popped = playing.pop(0)
    # autoclear
    from PriyaMusic.utils.stream.autoclear import auto_clean
    await auto_clean(popped)

    if not playing:
        await Priya.stop_stream(chat_id)
        return

    # play next
    nxt = playing[0]
    file = nxt["file"]
    video = nxt["streamtype"] == "video"
    title = nxt["title"]
    user = nxt["by"]
    nxt["played"] = 0

    from PriyaMusic.utils.inline.play import stream_markup
    from pyrogram.types import InlineKeyboardMarkup
    from strings import get_string
    from PriyaMusic.utils.database import get_lang
    lang = await get_lang(chat_id)
    _ = get_string(lang)

    try:
        if "vid_" in file:
            from PriyaMusic import YouTube
            n, file = await YouTube.video(nxt["vidid"], True)
            if n == 0:
                playing.pop(0)
                await Priya.stop_stream(chat_id)
                return
        await Priya.skip_stream(chat_id, file, video=video)
        await music_on(chat_id)

        from PriyaMusic.utils.thumbnails import get_thumb
        img = await get_thumb(nxt["vidid"]) if nxt["vidid"] not in ("telegram", "soundcloud") else config.YOUTUBE_IMG_URL
        button = stream_markup(_, chat_id)
        mystic = await app.send_photo(
            nxt.get("chat_id", chat_id),
            photo=img,
            caption=_["stream_1"].format(
                f"https://t.me/{app.username}?start=info_{nxt['vidid']}",
                title[:23],
                nxt["dur"],
                user,
            ),
            reply_markup=InlineKeyboardMarkup(button),
        )
        playing[0]["mystic"] = mystic
    except Exception:
        await Priya.stop_stream(chat_id)


Priya = _PriyaCall()
