import socket
import time

import heroku3
from pyrogram import filters

import config
from PriyaMusic.core.mongo import mongodb
from .logging import LOGGER

SUDOERS = filters.user()
HAPP = None
_boot_ = time.time()

XCB = [
    "/", "@", ".", "com", ":", "git", "heroku",
    "push", str(config.HEROKU_API_KEY), "https",
    str(config.HEROKU_APP_NAME), "HEAD", "master",
]


def is_heroku() -> bool:
    return "heroku" in socket.getfqdn()


def dbb():
    global db
    db = {}
    LOGGER(__name__).info("Local database initialised.")


async def sudo():
    global SUDOERS
    SUDOERS.add(config.OWNER_ID)
    sudoersdb = mongodb.sudoers
    doc = await sudoersdb.find_one({"sudo": "sudo"})
    sudoers = [] if not doc else doc.get("sudoers", [])
    if config.OWNER_ID not in sudoers:
        sudoers.append(config.OWNER_ID)
        await sudoersdb.update_one(
            {"sudo": "sudo"},
            {"$set": {"sudoers": sudoers}},
            upsert=True,
        )
    for uid in sudoers:
        SUDOERS.add(uid)
    LOGGER(__name__).info("Sudoers loaded.")


def heroku():
    global HAPP
    if is_heroku() and config.HEROKU_API_KEY and config.HEROKU_APP_NAME:
        try:
            h = heroku3.from_key(config.HEROKU_API_KEY)
            HAPP = h.app(config.HEROKU_APP_NAME)
            LOGGER(__name__).info("Heroku app configured.")
        except Exception as e:
            LOGGER(__name__).warning(f"Heroku config error: {e}")
