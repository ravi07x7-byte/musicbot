import os
import re

import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from PriyaMusic import app
from config import YOUTUBE_IMG_URL

try:
    from py_yt import VideosSearch
except ImportError:
    from youtubesearchpython.__future__ import VideosSearch

_FONT_PATH = "PriyaMusic/assets/"


def _resize(max_w, max_h, img):
    wr, hr = max_w / img.size[0], max_h / img.size[1]
    return img.resize((int(wr * img.size[0]), int(hr * img.size[1])))


def _crop_circle(img, size=400, border=20):
    half_w, half_h = img.size[0] / 2, img.size[1] / 2
    larger = int(size * 1.5)
    img = img.crop((
        half_w - larger / 2, half_h - larger / 2,
        half_w + larger / 2, half_h + larger / 2,
    ))
    img = img.resize((size - 2 * border, size - 2 * border))
    result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    mask = Image.new("L", (size - 2 * border, size - 2 * border), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size - 2 * border, size - 2 * border), fill=255)
    result.paste(img, (border, border), mask)
    border_mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(border_mask).ellipse((0, 0, size, size), fill=255)
    return Image.composite(result, Image.new("RGBA", result.size, (0, 0, 0, 0)), border_mask)


def _truncate(text: str):
    words = text.split()
    line1, line2 = "", ""
    for w in words:
        if len(line1) + len(w) < 30:
            line1 += " " + w
        elif len(line2) + len(w) < 30:
            line2 += " " + w
    return line1.strip(), line2.strip()


async def get_thumb(videoid: str) -> str:
    cache_path = f"cache/{videoid}_v4.png"
    if os.path.isfile(cache_path):
        return cache_path

    url = f"https://www.youtube.com/watch?v={videoid}"
    results = VideosSearch(url, limit=1)
    data = (await results.next())["result"]
    if not data:
        return YOUTUBE_IMG_URL

    r = data[0]
    title = re.sub(r"\W+", " ", r.get("title", "Unknown")).title()
    duration = r.get("duration", "0:00")
    views = r.get("viewCount", {}).get("short", "Unknown")
    channel = r.get("channel", {}).get("name", "Unknown")
    thumbnail = r["thumbnails"][0]["url"].split("?")[0]

    tmp = f"cache/thumb_{videoid}.png"
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                async with aiofiles.open(tmp, "wb") as f:
                    await f.write(await resp.read())

    if not os.path.isfile(tmp):
        return YOUTUBE_IMG_URL

    yt = Image.open(tmp)
    bg = _resize(1280, 720, yt).convert("RGBA")
    bg = bg.filter(ImageFilter.BoxBlur(20))
    bg = ImageEnhance.Brightness(bg).enhance(0.6)
    draw = ImageDraw.Draw(bg)

    try:
        font_bold = ImageFont.truetype(_FONT_PATH + "font3.ttf", 45)
        font_reg = ImageFont.truetype(_FONT_PATH + "font2.ttf", 30)
    except Exception:
        font_bold = font_reg = ImageFont.load_default()

    circle = _crop_circle(yt, 400, 20).resize((400, 400))
    bg.paste(circle, (120, 160), circle)

    tx = 565
    t1, t2 = _truncate(title)
    draw.text((tx, 180), t1, fill=(255, 255, 255), font=font_bold)
    draw.text((tx, 230), t2, fill=(255, 255, 255), font=font_bold)
    draw.text((tx, 320), f"{channel}  |  {views[:23]}", fill=(255, 255, 255), font=font_reg)

    # Progress bar
    red_end = tx + int(580 * 0.6)
    draw.line([(tx, 380), (red_end, 380)], fill="red", width=9)
    draw.line([(red_end, 380), (tx + 580, 380)], fill="white", width=8)
    r = 10
    draw.ellipse([red_end - r, 380 - r, red_end + r, 380 + r], fill="red")
    draw.text((tx, 400), "00:00", fill=(255, 255, 255), font=font_reg)
    draw.text((1080, 400), duration, fill=(255, 255, 255), font=font_reg)

    # Play icons
    icons_path = "PriyaMusic/assets/play_icons.png"
    if os.path.isfile(icons_path):
        icons = Image.open(icons_path).resize((580, 62))
        bg.paste(icons, (tx, 450), icons)

    try:
        os.remove(tmp)
    except Exception:
        pass

    bg.save(cache_path)
    return cache_path
