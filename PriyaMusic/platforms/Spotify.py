import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython.__future__ import VideosSearch
import config


class SpotifyAPI:
    def __init__(self):
        self.regex = r"^(https:\/\/open\.spotify\.com\/)(.*)$"
        self._sp = None
        if config.SPOTIFY_CLIENT_ID and config.SPOTIFY_CLIENT_SECRET:
            try:
                ccm = SpotifyClientCredentials(
                    config.SPOTIFY_CLIENT_ID, config.SPOTIFY_CLIENT_SECRET
                )
                self._sp = spotipy.Spotify(client_credentials_manager=ccm)
            except Exception:
                pass

    async def valid(self, link: str) -> bool:
        return bool(re.search(self.regex, link))

    async def _search_yt(self, query: str):
        results = VideosSearch(query, limit=1)
        for r in (await results.next())["result"]:
            return {
                "title": r["title"],
                "link": r["link"],
                "vidid": r["id"],
                "duration_min": r["duration"],
                "thumb": r["thumbnails"][0]["url"].split("?")[0],
            }, r["id"]
        return None, None

    async def track(self, link: str):
        if not self._sp:
            return None, None
        t = self._sp.track(link)
        query = t["name"] + " " + " ".join(
            a["name"] for a in t["artists"] if "Various Artists" not in a["name"]
        )
        return await self._search_yt(query)

    async def playlist(self, url: str):
        if not self._sp:
            return [], ""
        pl = self._sp.playlist(url)
        results = []
        for item in pl["tracks"]["items"]:
            t = item.get("track")
            if not t:
                continue
            query = t["name"] + " " + " ".join(
                a["name"] for a in t["artists"] if "Various Artists" not in a["name"]
            )
            results.append(query)
        return results, pl["id"]

    async def album(self, url: str):
        if not self._sp:
            return [], ""
        al = self._sp.album(url)
        results = []
        for item in al["tracks"]["items"]:
            query = item["name"] + " " + " ".join(
                a["name"] for a in item["artists"] if "Various Artists" not in a["name"]
            )
            results.append(query)
        return results, al["id"]

    async def artist(self, url: str):
        if not self._sp:
            return [], ""
        info = self._sp.artist(url)
        tops = self._sp.artist_top_tracks(url)
        results = []
        for item in tops["tracks"]:
            query = item["name"] + " " + " ".join(
                a["name"] for a in item["artists"] if "Various Artists" not in a["name"]
            )
            results.append(query)
        return results, info["id"]
