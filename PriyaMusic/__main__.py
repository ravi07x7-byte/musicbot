import asyncio
import importlib

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from PriyaMusic import LOGGER, app, userbot
from PriyaMusic.core.call import Priya
from PriyaMusic.misc import sudo
from PriyaMusic.plugins import ALL_MODULES
from PriyaMusic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS


async def init():
    if not config.STRING_SESSION:
        LOGGER(__name__).error("STRING_SESSION not set. Exiting.")
        exit(1)

    await sudo()

    # Load banned users into memory filter
    try:
        for uid in await get_gbanned():
            BANNED_USERS.add(uid)
        for uid in await get_banned_users():
            BANNED_USERS.add(uid)
    except Exception:
        pass

    await app.start()

    for module in ALL_MODULES:
        importlib.import_module("PriyaMusic.plugins" + module)
    LOGGER("PriyaMusic.plugins").info(f"Loaded {len(ALL_MODULES)} modules.")

    await userbot.start()

    # Register PyTgCalls for each assistant
    for num, client in userbot._clients:
        call_instance = Priya.register(num, client)

    await Priya.start()

    # Verify log group voice chat is accessible
    try:
        await Priya.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("PriyaMusic").error(
            "Please turn on the video chat in your log group/channel.\nStopping..."
        )
        exit(1)
    except Exception:
        pass

    await Priya.decorators()

    LOGGER("PriyaMusic").info(
        "✅ PriyaMusic started successfully! Check your log group."
    )

    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("PriyaMusic").info("PriyaMusic stopped.")


if __name__ == "__main__":
    asyncio.run(init())
