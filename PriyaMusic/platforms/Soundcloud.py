import os
from yt_dlp import YoutubeDL
from PriyaMusic.utils.formatters import seconds_to_min


class SoundAPI:
    def __init__(self):
        self.opts = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "format": "best",
            "retries": 3,
            "nooverwrites": False,
            "continuedl": True,
            "quiet": True,
        }

    async def valid(self, link: str) -> bool:
        return "soundcloud" in link.lower()

    async def download(self, url: str):
        with YoutubeDL(self.opts) as ydl:
            try:
                info = ydl.extract_info(url)
            except Exception:
                return False, None
        path = os.path.join("downloads", f"{info['id']}.{info['ext']}")
        details = {
            "title": info.get("title", "SoundCloud Track"),
            "duration_sec": info.get("duration", 0),
            "duration_min": seconds_to_min(info.get("duration", 0)),
            "uploader": info.get("uploader", "Unknown"),
            "filepath": path,
        }
        return details, path
