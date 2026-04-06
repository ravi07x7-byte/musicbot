import asyncio
import os
import time
from typing import Union

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Voice

import config
from PriyaMusic import app
from PriyaMusic.utils.formatters import check_duration, convert_bytes, get_readable_time, seconds_to_min


class TeleAPI:
    def __init__(self):
        self.chars_limit = 4096

    async def get_filename(self, file, audio: bool = False) -> str:
        try:
            name = file.file_name
            if not name:
                raise AttributeError
        except AttributeError:
            name = "Telegram Audio" if audio else "Telegram Video"
        return name

    async def get_duration(self, filex, file_path: str) -> str:
        try:
            return seconds_to_min(filex.duration)
        except Exception:
            try:
                dur = await asyncio.get_event_loop().run_in_executor(
                    None, check_duration, file_path
                )
                return seconds_to_min(dur)
            except Exception:
                return "Unknown"

    async def get_filepath(self, audio=None, video=None) -> str:
        if audio:
            try:
                ext = audio.file_name.split(".")[-1] if not isinstance(audio, Voice) else "ogg"
            except Exception:
                ext = "ogg"
            return os.path.join(os.path.realpath("downloads"), f"{audio.file_unique_id}.{ext}")
        if video:
            try:
                ext = video.file_name.split(".")[-1]
            except Exception:
                ext = "mp4"
            return os.path.join(os.path.realpath("downloads"), f"{video.file_unique_id}.{ext}")

    async def download(self, _, message, mystic, fname: str) -> bool:
        if os.path.exists(fname):
            return True

        speed_counter = {}

        async def progress(current, total):
            if current == total:
                return
            now = time.time()
            start = speed_counter.get(message.id, now)
            elapsed = now - start or 1
            pct = int(current * 100 / total)
            speed = current / elapsed
            eta = get_readable_time(int((total - current) / (speed or 1)))
            upl = InlineKeyboardMarkup([[
                InlineKeyboardButton("Cancel", callback_data="stop_downloading")
            ]])
            if pct % 20 == 0:
                try:
                    await mystic.edit_text(
                        _["tg_1"].format(
                            app.mention,
                            convert_bytes(total),
                            convert_bytes(current),
                            pct,
                            convert_bytes(speed),
                            eta,
                        ),
                        reply_markup=upl,
                    )
                except Exception:
                    pass

        speed_counter[message.id] = time.time()
        try:
            await app.download_media(
                message.reply_to_message,
                file_name=fname,
                progress=progress,
            )
            elapsed = get_readable_time(int(time.time() - speed_counter[message.id]))
            await mystic.edit_text(_["tg_2"].format(elapsed))
        except Exception:
            await mystic.edit_text(_["tg_3"])
            return False

        from config import lyrical
        verify = lyrical.get(mystic.id)
        if not verify:
            return False
        lyrical.pop(mystic.id, None)
        return True
