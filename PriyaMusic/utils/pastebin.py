import aiohttp

_BASE = "https://batbin.me/"


async def PriyaBin(text: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{_BASE}api/v2/paste", data=text) as resp:
            try:
                data = await resp.json()
                if data.get("success"):
                    return _BASE + data["message"]
            except Exception:
                pass
    return _BASE
