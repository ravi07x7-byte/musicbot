import re
from typing import Union
import aiohttp
from bs4 import BeautifulSoup
from youtubesearchpython.__future__ import VideosSearch


class RessoAPI:
    def __init__(self):
        self.regex = r"^(https:\/\/m\.resso\.com\/)(.*)$"

    async def valid(self, link: str) -> bool:
        return bool(re.search(self.regex, link))

    async def track(self, url: str, playid: Union[bool, str] = None):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return False, None
                html = await resp.text()
        soup = BeautifulSoup(html, "html.parser")
        title = None
        for tag in soup.find_all("meta"):
            if tag.get("property") == "og:title":
                title = tag.get("content")
        if not title:
            return False, None
        results = VideosSearch(title, limit=1)
        for r in (await results.next())["result"]:
            details = {
                "title": r["title"],
                "link": r["link"],
                "vidid": r["id"],
                "duration_min": r["duration"],
                "thumb": r["thumbnails"][0]["url"].split("?")[0],
            }
            return details, r["id"]
