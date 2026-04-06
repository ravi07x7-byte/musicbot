import re
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# ─── Required ───────────────────────────────────────────────
API_ID = int(getenv("API_ID", 0))
API_HASH = getenv("API_HASH", "")
BOT_TOKEN = getenv("BOT_TOKEN", "")
MONGO_DB_URI = getenv("MONGO_DB_URI", "")
OWNER_ID = int(getenv("OWNER_ID", 0))
STRING_SESSION = getenv("STRING_SESSION", "")
LOGGER_ID = int(getenv("LOGGER_ID", 0))

# ─── Optional assistants ────────────────────────────────────
STRING2 = getenv("STRING_SESSION2")
STRING3 = getenv("STRING_SESSION3")
STRING4 = getenv("STRING_SESSION4")
STRING5 = getenv("STRING_SESSION5")

# ─── Bot identity (owner customisable) ─────────────────────
BOT_NAME = getenv("BOT_NAME", "PriyaMusic")
BOT_USERNAME = getenv("BOT_USERNAME", "")  # without @

# ─── Support links ──────────────────────────────────────────
SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/yourchannel")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/yoursupport")

# ─── Heroku / Railway ───────────────────────────────────────
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")
UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/yourusername/PriyaMusic")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv("GIT_TOKEN", "")

# ─── Spotify ────────────────────────────────────────────────
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET")

# ─── Limits ─────────────────────────────────────────────────
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 10000))
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", 104857600))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", 1073741824))

# ─── Feature flags ──────────────────────────────────────────
AUTO_LEAVING_ASSISTANT = bool(getenv("AUTO_LEAVING_ASSISTANT", False))
AUTOPLAY_ENABLED = bool(getenv("AUTOPLAY_ENABLED", True))
AUTOPLAY_IDLE_MINUTES = int(getenv("AUTOPLAY_IDLE_MINUTES", 300))  # 5 hours

# ─── Images ─────────────────────────────────────────────────
START_IMG_URL = getenv("START_IMG_URL", "https://telegra.ph/file/d30d11c4365c025c25e3e.jpg")
PING_IMG_URL = getenv("PING_IMG_URL", "https://telegra.ph/file/d30d11c4365c025c25e3e.jpg")
PLAYLIST_IMG_URL = getenv("PLAYLIST_IMG_URL", "https://telegra.ph/file/d30d11c4365c025c25e3e.jpg")
STATS_IMG_URL = getenv("STATS_IMG_URL", "https://telegra.ph/file/d30d11c4365c025c25e3e.jpg")
YOUTUBE_IMG_URL = "https://telegra.ph/file/d30d11c4365c025c25e3e.jpg"
STREAM_IMG_URL = "https://telegra.ph/file/d30d11c4365c025c25e3e.jpg"
TELEGRAM_AUDIO_URL = "https://telegra.ph/file/d30d11c4365c025c25e3e.jpg"
TELEGRAM_VIDEO_URL = "https://telegra.ph/file/d30d11c4365c025c25e3e.jpg"
SOUNDCLOUD_IMG_URL = "https://telegra.ph/file/d30d11c4365c025c25e3e.jpg"

# ─── Runtime state (do not edit) ────────────────────────────
BANNED_USERS = filters.user()
adminlist: dict = {}
lyrical: dict = {}
votemode: dict = {}
autoclean: list = []
confirmer: dict = {}


def time_to_seconds(time: str) -> int:
    parts = str(time).split(":")
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(parts)))


DURATION_LIMIT = time_to_seconds(f"{DURATION_LIMIT_MIN}:00")

# ─── Validation ─────────────────────────────────────────────
for _url_var, _url_val in [("SUPPORT_CHANNEL", SUPPORT_CHANNEL), ("SUPPORT_CHAT", SUPPORT_CHAT)]:
    if _url_val and not re.match(r"(?:http|https)://", _url_val):
        raise SystemExit(f"[ERROR] {_url_var} must start with https://")

if not all([API_ID, API_HASH, BOT_TOKEN, MONGO_DB_URI, OWNER_ID, STRING_SESSION, LOGGER_ID]):
    raise SystemExit(
        "[ERROR] Missing required env vars: API_ID, API_HASH, BOT_TOKEN, "
        "MONGO_DB_URI, OWNER_ID, STRING_SESSION, LOGGER_ID"
    )
