from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message

from PriyaMusic import app
from PriyaMusic.core.call import Priya
from PriyaMusic.utils import bot_sys_stats
from PriyaMusic.utils.decorators import language
from PriyaMusic.utils.inline import supp_markup
from config import BANNED_USERS, PING_IMG_URL


@app.on_message(filters.command(["ping", "alive"]) & ~BANNED_USERS)
@language
async def ping_cmd(client, message: Message, _):
    start = datetime.now()
    response = await message.reply_photo(
        photo=PING_IMG_URL,
        caption=_["ping_1"].format(app.mention),
    )
    pytgping = await Priya.ping()
    UP, CPU, RAM, DISK = await bot_sys_stats()
    resp_ms = (datetime.now() - start).microseconds / 1000
    await response.edit_text(
        _["ping_2"].format(resp_ms, app.mention, UP, RAM, CPU, DISK, pytgping),
        reply_markup=supp_markup(_),
    )
