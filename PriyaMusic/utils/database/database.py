"""
Central database layer for PriyaMusic.
All MongoDB operations go through here — no direct collection access elsewhere.
"""

from typing import Any

from PriyaMusic.core.mongo import mongodb

# Collections
_chats = mongodb.chats
_users = mongodb.users
_sudo = mongodb.sudoers
_banned = mongodb.banned
_gbanned = mongodb.gbanned
_active = mongodb.active_voice
_active_video = mongodb.active_video
_settings = mongodb.settings
_autoplay = mongodb.autoplay
_lang = mongodb.language
_auth = mongodb.authusers
_blacklist = mongodb.blacklist
_maintenance = mongodb.maintenance
_loop = mongodb.loop
_skip = mongodb.skipmode
_playmode = mongodb.playmode
_upvote = mongodb.upvote


# ─── Served chats / users ───────────────────────────────────
async def add_served_chat(chat_id: int):
    await _chats.update_one({"chat_id": chat_id}, {"$set": {"chat_id": chat_id}}, upsert=True)

async def add_served_user(user_id: int):
    await _users.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)

async def get_served_chats() -> list:
    return await _chats.find().to_list(length=None)

async def get_served_users() -> list:
    return await _users.find().to_list(length=None)


# ─── Active voice/video chats ───────────────────────────────
async def add_active_chat(chat_id: int):
    await _active.update_one({"chat_id": chat_id}, {"$set": {"chat_id": chat_id}}, upsert=True)

async def remove_active_chat(chat_id: int):
    await _active.delete_one({"chat_id": chat_id})

async def get_active_chats() -> list[int]:
    docs = await _active.find().to_list(length=None)
    return [d["chat_id"] for d in docs]

async def is_active_chat(chat_id: int) -> bool:
    return bool(await _active.find_one({"chat_id": chat_id}))

async def add_active_video_chat(chat_id: int):
    await _active_video.update_one({"chat_id": chat_id}, {"$set": {"chat_id": chat_id}}, upsert=True)

async def remove_active_video_chat(chat_id: int):
    await _active_video.delete_one({"chat_id": chat_id})

async def get_active_video_chats() -> list[int]:
    docs = await _active_video.find().to_list(length=None)
    return [d["chat_id"] for d in docs]


# ─── Music state ────────────────────────────────────────────
_music_on: set[int] = set()

async def music_on(chat_id: int):
    _music_on.add(chat_id)

async def music_off(chat_id: int):
    _music_on.discard(chat_id)

async def is_music_playing(chat_id: int) -> bool:
    return chat_id in _music_on


# ─── Sudoers ────────────────────────────────────────────────
async def add_sudo(user_id: int) -> bool:
    doc = await _sudo.find_one({"sudo": "sudo"}) or {}
    sudoers = doc.get("sudoers", [])
    if user_id in sudoers:
        return False
    sudoers.append(user_id)
    await _sudo.update_one({"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True)
    return True

async def remove_sudo(user_id: int) -> bool:
    doc = await _sudo.find_one({"sudo": "sudo"}) or {}
    sudoers = doc.get("sudoers", [])
    if user_id not in sudoers:
        return False
    sudoers.remove(user_id)
    await _sudo.update_one({"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True)
    return True

async def get_sudoers() -> list[int]:
    doc = await _sudo.find_one({"sudo": "sudo"}) or {}
    return doc.get("sudoers", [])


# ─── Banned / Gbanned users ─────────────────────────────────
async def add_banned_user(user_id: int):
    await _banned.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)

async def remove_banned_user(user_id: int):
    await _banned.delete_one({"user_id": user_id})

async def is_banned_user(user_id: int) -> bool:
    return bool(await _banned.find_one({"user_id": user_id}))

async def get_banned_users() -> list[int]:
    docs = await _banned.find().to_list(length=None)
    return [d["user_id"] for d in docs]

async def get_banned_count() -> int:
    return await _banned.count_documents({})

async def add_gbanned_user(user_id: int):
    await _gbanned.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)

async def remove_gbanned_user(user_id: int):
    await _gbanned.delete_one({"user_id": user_id})

async def is_gbanned_user(user_id: int) -> bool:
    return bool(await _gbanned.find_one({"user_id": user_id}))

async def get_gbanned() -> list[int]:
    docs = await _gbanned.find().to_list(length=None)
    return [d["user_id"] for d in docs]


# ─── Blacklist chats ────────────────────────────────────────
async def blacklist_chat(chat_id: int) -> bool:
    await _blacklist.update_one({"chat_id": chat_id}, {"$set": {"chat_id": chat_id}}, upsert=True)
    return True

async def whitelist_chat(chat_id: int) -> bool:
    await _blacklist.delete_one({"chat_id": chat_id})
    return True

async def blacklisted_chats() -> list[int]:
    docs = await _blacklist.find().to_list(length=None)
    return [d["chat_id"] for d in docs]


# ─── Language ───────────────────────────────────────────────
async def get_lang(chat_id: int) -> str:
    doc = await _lang.find_one({"chat_id": chat_id})
    return doc.get("lang", "en") if doc else "en"

async def set_lang(chat_id: int, lang: str):
    await _lang.update_one({"chat_id": chat_id}, {"$set": {"lang": lang}}, upsert=True)


# ─── Auth users ─────────────────────────────────────────────
async def save_authuser(chat_id: int, token: str, data: dict):
    await _auth.update_one({"chat_id": chat_id, "token": token}, {"$set": data}, upsert=True)

async def delete_authuser(chat_id: int, token: str):
    result = await _auth.delete_one({"chat_id": chat_id, "token": token})
    return result.deleted_count > 0

async def get_authuser_names(chat_id: int) -> list[str]:
    docs = await _auth.find({"chat_id": chat_id}).to_list(length=None)
    return [d["token"] for d in docs]

async def get_authuser(chat_id: int, token: str) -> dict:
    return await _auth.find_one({"chat_id": chat_id, "token": token}) or {}


# ─── Settings: loop, playmode, skipmode ─────────────────────
async def get_loop(chat_id: int) -> int:
    doc = await _loop.find_one({"chat_id": chat_id})
    return doc.get("loop", 0) if doc else 0

async def set_loop(chat_id: int, count: int):
    await _loop.update_one({"chat_id": chat_id}, {"$set": {"loop": count}}, upsert=True)

async def get_playmode(chat_id: int) -> str:
    doc = await _playmode.find_one({"chat_id": chat_id})
    return doc.get("mode", "Direct") if doc else "Direct"

async def set_playmode(chat_id: int, mode: str):
    await _playmode.update_one({"chat_id": chat_id}, {"$set": {"mode": mode}}, upsert=True)

async def is_skipmode(chat_id: int) -> bool:
    doc = await _skip.find_one({"chat_id": chat_id})
    return bool(doc.get("enabled", False)) if doc else False

async def get_upvote_count(chat_id: int) -> int:
    doc = await _upvote.find_one({"chat_id": chat_id})
    return doc.get("count", 3) if doc else 3


# ─── Maintenance ────────────────────────────────────────────
async def is_maintenance() -> bool:
    doc = await _maintenance.find_one({"id": 1})
    return bool(doc.get("on", False)) if doc else True  # True = running

async def maintenance_on():
    await _maintenance.update_one({"id": 1}, {"$set": {"on": True}}, upsert=True)

async def maintenance_off():
    await _maintenance.update_one({"id": 1}, {"$set": {"on": False}}, upsert=True)


# ─── Settings toggles (logger, etc.) ───────────────────────
async def is_on_off(num: int) -> bool:
    doc = await _settings.find_one({"num": num})
    return bool(doc.get("on", False)) if doc else False

async def add_on(num: int):
    await _settings.update_one({"num": num}, {"$set": {"on": True}}, upsert=True)

async def add_off(num: int):
    await _settings.update_one({"num": num}, {"$set": {"on": False}}, upsert=True)


# ─── Autoplay ───────────────────────────────────────────────
async def set_autoplay(chat_id: int, enabled: bool):
    await _autoplay.update_one({"chat_id": chat_id}, {"$set": {"enabled": enabled}}, upsert=True)

async def get_autoplay(chat_id: int) -> bool:
    doc = await _autoplay.find_one({"chat_id": chat_id})
    return bool(doc.get("enabled", True)) if doc else True

async def set_autoplay_category(chat_id: int, category: str):
    await _autoplay.update_one({"chat_id": chat_id}, {"$set": {"category": category}}, upsert=True)

async def get_autoplay_category(chat_id: int) -> str:
    doc = await _autoplay.find_one({"chat_id": chat_id})
    return doc.get("category", "pop") if doc else "pop"


# ─── Channel play mode ──────────────────────────────────────
_cmode: dict[int, int] = {}

async def get_cmode(chat_id: int) -> int | None:
    return _cmode.get(chat_id)

async def set_cmode(chat_id: int, linked_id: int | None):
    if linked_id is None:
        _cmode.pop(chat_id, None)
    else:
        _cmode[chat_id] = linked_id


# ─── Nonadmin chat ──────────────────────────────────────────
_nonadmin: set[int] = set()

async def is_nonadmin_chat(chat_id: int) -> bool:
    return chat_id in _nonadmin

async def nonadmin_on(chat_id: int):
    _nonadmin.add(chat_id)

async def nonadmin_off(chat_id: int):
    _nonadmin.discard(chat_id)


# ─── Autoend ────────────────────────────────────────────────
_autoend_flag = False

async def autoend_on():
    global _autoend_flag
    _autoend_flag = True

async def autoend_off():
    global _autoend_flag
    _autoend_flag = False

async def is_autoend() -> bool:
    return _autoend_flag


# ─── Assistant assignment ───────────────────────────────────
_chat_assistant: dict[int, int] = {}

async def get_assistant(chat_id: int) -> int:
    return _chat_assistant.get(chat_id, 1)

async def set_assistant(chat_id: int, num: int):
    _chat_assistant[chat_id] = num

async def connect_to_chat(user_id: int, chat_id) -> bool:
    # placeholder — extend as needed
    return True
