"""
Security layer for PriyaMusic.
- Alerts owner on suspicious activity
- Detects unknown /eval, /sh attempts
- Logs all intrusion attempts to log channel and pins them
"""

import asyncio
from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message

import config
from PriyaMusic import app
from PriyaMusic.misc import SUDOERS


async def alert_owner(text: str, pin: bool = False):
    """Send an alert to LOGGER_ID and optionally pin it. Also DM owner."""
    full_text = f"⚠️ <b>PriyaMusic Alert</b>\n{datetime.now().strftime('%d %b %Y %H:%M:%S')}\n\n{text}"
    try:
        msg = await app.send_message(config.LOGGER_ID, full_text, disable_web_page_preview=True)
        if pin:
            try:
                await msg.pin(disable_notification=False)
            except Exception:
                pass
    except Exception:
        pass
    try:
        await app.send_message(config.OWNER_ID, full_text, disable_web_page_preview=True)
    except Exception:
        pass


def intrusion_guard(mystic):
    """Decorator: blocks non-owner access and logs attempt."""
    async def wrapper(client, message: Message):
        if message.from_user and message.from_user.id not in SUDOERS:
            await alert_owner(
                f"🚨 <b>Intrusion attempt</b>\n"
                f"Command: <code>{message.text[:100]}</code>\n"
                f"User: {message.from_user.mention} (<code>{message.from_user.id}</code>)\n"
                f"Chat: {message.chat.title} (<code>{message.chat.id}</code>)",
                pin=True,
            )
            return await message.reply_text("⛔ Access denied. This attempt has been logged.")
        return await mystic(client, message)
    return wrapper


# ─── Watch for eval/sh from non-owners ──────────────────────
@app.on_message(
    filters.command(["eval", "sh", "exec", "terminal"])
    & ~filters.user(config.OWNER_ID)
)
async def catch_eval(client, message: Message):
    await alert_owner(
        f"🚨 <b>Unauthorized eval/sh attempt</b>\n"
        f"Command: <code>{message.text[:200]}</code>\n"
        f"User: {message.from_user.mention} (<code>{message.from_user.id}</code>)\n"
        f"Chat: {message.chat.title} (<code>{message.chat.id}</code>)",
        pin=True,
    )
    await message.reply_text("⛔ This command is restricted. Attempt logged.")


# ─── Watch for code injection in bot messages ────────────────
_SUSPICIOUS = ["import os", "subprocess", "__import__", "exec(", "eval(", "open("]


@app.on_message(filters.text & filters.group)
async def watch_injection(client, message: Message):
    if not message.text:
        return
    lower = message.text.lower()
    if any(kw in lower for kw in _SUSPICIOUS):
        if message.from_user and message.from_user.id not in SUDOERS:
            await alert_owner(
                f"🔍 Suspicious message detected\n"
                f"User: {message.from_user.mention} (<code>{message.from_user.id}</code>)\n"
                f"Chat: {message.chat.title} (<code>{message.chat.id}</code>)\n"
                f"Text: <code>{message.text[:300]}</code>"
            )
