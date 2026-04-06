import asyncio
import os
import re
from typing import Union

import aiohttp
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message

from PriyaMusic.utils.formatters import time_to_seconds
from PriyaMusic import LOGGER

try:
    from py_yt import VideosSearch
except ImportError:
    from youtubesearchpython.__future__ import VideosSearch

_DL_DIR = "downloads"
os.makedirs(_DL_DIR, exist_ok=True)


async def _shell(cmd: str) -> str:
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    out, err = await proc.communicate()
    if err:
        decoded = err.decode("utf-8", errors="replace")
        if "unavailable videos are hidden" in decoded.lower():
            return out.decode("utf-8", errors="replace")
        return decoded
    return out.decode("utf-8", errors="replace")


async def _download_file(url: str, path: str, params: dict) -> str | None:
    """Download via yt-dlp in a thread pool."""
    def _dl():
        with yt_dlp.YoutubeDL(params) as ydl:
            ydl.download([url])
    try:
        await asyncio.get_event_loop().run_in_executor(None, _dl)
        if os.path.isfile(path) and os.path.getsize(path) > 0:
            return path
    except Exception as e:
        LOGGER(__name__).warning(f"yt-dlp download error: {e}")
    return None


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="

    async def exists(self, link: str, videoid: bool = False) -> bool:
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message: Message) -> str | None:
        for msg in [message, message.reply_to_message] if message.reply_to_message else [message]:
            if not msg:
                continue
            for ent in (msg.entities or []):
                if ent.type == MessageEntityType.URL:
                    text = msg.text or msg.caption or ""
                    return text[ent.offset: ent.offset + ent.length]
            for ent in (msg.caption_entities or []):
                if ent.type == MessageEntityType.TEXT_LINK:
                    return ent.url
        return None

    async def details(self, link: str, videoid: bool = False):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for r in (await results.next())["result"]:
            title = r["title"]
            duration_min = r["duration"]
            thumbnail = r["thumbnails"][0]["url"].split("?")[0]
            vidid = r["id"]
            duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: bool = False) -> str:
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for r in (await results.next())["result"]:
            return r["title"]

    async def duration(self, link: str, videoid: bool = False) -> str:
        if videoid:
            link = self.base + link
        results = VideosSearch(link, limit=1)
        for r in (await results.next())["result"]:
            return r["duration"]

    async def thumbnail(self, link: str, videoid: bool = False) -> str:
        if videoid:
            link = self.base + link
        results = VideosSearch(link, limit=1)
        for r in (await results.next())["result"]:
            return r["thumbnails"][0]["url"].split("?")[0]

    async def track(self, link: str, videoid: bool = False):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for r in (await results.next())["result"]:
            details = {
                "title": r["title"],
                "link": r["link"],
                "vidid": r["id"],
                "duration_min": r["duration"],
                "thumb": r["thumbnails"][0]["url"].split("?")[0],
            }
            return details, r["id"]

    async def slider(self, link: str, query_type: int = 0, videoid: bool = False):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=10)
        data = (await results.next()).get("result", [])
        if not data or query_type >= len(data):
            return None
        r = data[query_type]
        return r["title"], r["duration"], r["thumbnails"][0]["url"].split("?")[0], r["id"]

    async def video(self, link: str, videoid: bool = False):
        if videoid:
            link = self.base + link
        path = os.path.join(_DL_DIR, f"{link.split('v=')[-1]}.mp4")
        opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": path,
            "quiet": True,
            "no_warnings": True,
        }
        result = await _download_file(link, path, opts)
        if result:
            return 1, result
        return 0, "Download failed"

    async def playlist(self, link: str, limit: int, user_id: int, videoid: bool = False):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        out = await _shell(
            f"yt-dlp -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link}"
        )
        return [v for v in out.split("\n") if v.strip()]

    async def formats(self, link: str, videoid: bool = False):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(link, download=False)
        fmts = []
        for fmt in info.get("formats", []):
            try:
                if "dash" not in str(fmt.get("format", "")).lower():
                    fmts.append({
                        "format": fmt["format"],
                        "filesize": fmt.get("filesize"),
                        "format_id": fmt["format_id"],
                        "ext": fmt["ext"],
                        "format_note": fmt.get("format_note", ""),
                        "yturl": link,
                    })
            except Exception:
                continue
        return fmts, link

    async def download(
        self,
        link: str,
        mystic,
        video: bool = None,
        videoid: bool = False,
        songaudio: bool = None,
        songvideo: bool = None,
        format_id: str = None,
        title: str = None,
    ):
        if videoid:
            link = self.base + link
        vid = link.split("v=")[-1].split("&")[0] if "v=" in link else link

        if video:
            path = os.path.join(_DL_DIR, f"{vid}.mp4")
            opts = {
                "format": "best[ext=mp4]/best",
                "outtmpl": path,
                "quiet": True,
                "no_warnings": True,
            }
        else:
            path = os.path.join(_DL_DIR, f"{vid}.mp3")
            opts = {
                "format": "bestaudio/best",
                "outtmpl": path,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
                "quiet": True,
                "no_warnings": True,
            }

        if os.path.isfile(path) and os.path.getsize(path) > 0:
            return path, True

        result = await _download_file(link, path, opts)
        if result:
            return result, True
        return None, False
