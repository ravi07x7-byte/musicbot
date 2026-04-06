from pyrogram import filters
from pyrogram.types import Message

from PriyaMusic import app
from PriyaMusic.utils.database import (
    delete_authuser,
    get_authuser,
    get_authuser_names,
    save_authuser,
)
from PriyaMusic.utils.decorators import AdminActual, language
from PriyaMusic.utils.extraction import extract_user
from PriyaMusic.utils.formatters import int_to_alpha
from PriyaMusic.utils.inline import close_markup
from config import BANNED_USERS, adminlist


@app.on_message(filters.command("auth") & filters.group & ~BANNED_USERS)
@AdminActual
async def auth_cmd(client, message: Message, _):
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text(_["general_1"])
    user = await extract_user(message)
    if not user:
        return await message.reply_text("User not found.")
    token = await int_to_alpha(user.id)
    existing = await get_authuser_names(message.chat.id)
    if len(existing) >= 25:
        return await message.reply_text(_["auth_1"])
    if token in existing:
        return await message.reply_text(_["auth_3"].format(user.mention))
    await save_authuser(message.chat.id, token, {
        "auth_user_id": user.id,
        "auth_name": user.first_name,
        "admin_id": message.from_user.id,
        "admin_name": message.from_user.first_name,
    })
    admins = adminlist.get(message.chat.id)
    if admins and user.id not in admins:
        admins.append(user.id)
    await message.reply_text(_["auth_2"].format(user.mention))


@app.on_message(filters.command("unauth") & filters.group & ~BANNED_USERS)
@AdminActual
async def unauth_cmd(client, message: Message, _):
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text(_["general_1"])
    user = await extract_user(message)
    if not user:
        return await message.reply_text("User not found.")
    token = await int_to_alpha(user.id)
    deleted = await delete_authuser(message.chat.id, token)
    admins = adminlist.get(message.chat.id)
    if admins and user.id in admins:
        admins.remove(user.id)
    if deleted:
        await message.reply_text(_["auth_4"].format(user.mention))
    else:
        await message.reply_text(_["auth_5"].format(user.mention))


@app.on_message(filters.command(["authlist", "authusers"]) & filters.group & ~BANNED_USERS)
@language
async def authlist_cmd(client, message: Message, _):
    tokens = await get_authuser_names(message.chat.id)
    if not tokens:
        return await message.reply_text(_["setting_4"] if "setting_4" in _ else "No auth users.")
    mystic = await message.reply_text(_["auth_6"])
    text = _["auth_7"].format(message.chat.title)
    j = 0
    for token in tokens:
        data = await get_authuser(message.chat.id, token)
        uid = data.get("auth_user_id")
        admin_id = data.get("admin_id")
        admin_name = data.get("admin_name", "Unknown")
        try:
            u = (await app.get_users(uid)).first_name
            j += 1
        except Exception:
            continue
        text += f"{j}➤ {u} [<code>{uid}</code>]\n"
        text += f"   {_['auth_8']} {admin_name} [<code>{admin_id}</code>]\n\n"
    await mystic.edit_text(text, reply_markup=close_markup(_))
