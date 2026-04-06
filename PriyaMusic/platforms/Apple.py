import re
from typing import Union
import aiohttp
from bs4 import BeautifulSoup
from youtubesearchpython.__future__ import VideosSearch


class AppleAPI:
    def __init__(self):
        self.regex = r"^(https:\/\/music\.apple\.com\/)(.*)$"
        self.base = "https://music.apple.com/in/playlist/"

    async def valid(self, link: str) -> bool:
        return bool(re.search(self.regex, link))

    async def track(self, url: str, playid: Union[bool, str] = None):
        if playid:
            url = self.base + url
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return False, None
                html = await resp.text()
        soup = BeautifulSoup(html, "html.parser")
        search = None
        for tag in soup.find_all("meta"):
            if tag.get("property") == "og:title":
                search = tag.get("content")
        if not search:
            return False, None
        results = VideosSearch(search, limit=1)
        for r in (await results.next())["result"]:
            details = {
                "title": r["title"],
                "link": r["link"],
                "vidid": r["id"],
                "duration_min": r["duration"],
                "thumb": r["thumbnails"][0]["url"].split("?")[0],
            }
            return details, r["id"]

    async def playlist(self, url: str, playid: Union[bool, str] = None):
        if playid:
            url = self.base + url
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return [], ""
                html = await resp.text()
        soup = BeautifulSoup(html, "html.parser")
        items = soup.find_all("meta", attrs={"property": "music:song"})
        results = []
        for item in items:
            try:
                name = item["content"].split("album/")[1].split("/")[0].replace("-", " ")
            except Exception:
                continue
            results.append(name)
        return results, url.split("playlist/")[1] if "playlist/" in url else ""
