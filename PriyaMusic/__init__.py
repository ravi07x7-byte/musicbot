from PriyaMusic.core.bot import Priya
from PriyaMusic.core.dir import dirr
from PriyaMusic.core.git import git
from PriyaMusic.core.userbot import Userbot
from PriyaMusic.misc import dbb, heroku

from .logging import LOGGER

dirr()
git()
dbb()
heroku()

app = Priya()
userbot = Userbot()

from .platforms import (
    AppleAPI,
    CarbonAPI,
    SoundAPI,
    SpotifyAPI,
    TeleAPI,
    YouTubeAPI,
)

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
