"""
Owner-only commands for PriyaMusic.
Only OWNER_ID can use these — sudo users cannot.
"""

import os
from pyrogram import filters
from pyrogram.types import Message

import config
from PriyaMusic import app
from PriyaMusic.utils.security import alert_owner
from config import OWNER_ID


def owner_only(mystic):
    async def wrapper(client, message: Message):
        if message.from_user.id != OWNER_ID:
            await alert_owner(
                f"🚨 Unauthorized owner command attempt\n"
                f"Command: <code>{message.text[:100]}</code>\n"
                f"User: {message.from_user.mention} (<code>{message.from_user.id}</code>)",
                pin=True,
            )
            return await message.reply_text("⛔ This command is for the bot owner only.")
        return await mystic(client, message)
    return wrapper


@app.on_message(filters.command("setbotname") & filters.private)
@owner_only
async def set_bot_name(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /setbotname <New Name>")
    new_name = message.text.split(None, 1)[1].strip()
    try:
        await app.update_profile(first_name=new_name)
        await message.reply_text(f"✅ Bot name changed to <b>{new_name}</b>.")
        await alert_owner(f"Bot name changed to: {new_name}")
    except Exception as e:
        await message.reply_text(f"Failed: {e}")


@app.on_message(filters.command("setbotbio") & filters.private)
@owner_only
async def set_bot_bio(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /setbotbio <bio text>")
    bio = message.text.split(None, 1)[1].strip()
    try:
        await app.update_profile(bio=bio)
        await message.reply_text(f"✅ Bio updated.")
    except Exception as e:
        await message.reply_text(f"Failed: {e}")


@app.on_message(filters.command("setbotphoto") & filters.private)
@owner_only
async def set_bot_photo(client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply_text("Reply to a photo.")
    path = await message.reply_to_message.download()
    try:
        await app.set_profile_photo(photo=path)
        await message.reply_text("✅ Profile photo updated.")
    except Exception as e:
        await message.reply_text(f"Failed: {e}")
    finally:
        try:
            os.remove(path)
        except Exception:
            pass


@app.on_message(filters.command("eval") & filters.private & filters.user(OWNER_ID))
async def eval_cmd(client, message: Message):
    import sys
    import traceback
    from io import StringIO
    from time import time

    if len(message.command) < 2:
        return await message.reply_text("Provide code to evaluate.")
    code = message.text.split(None, 1)[1]

    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = buf = StringIO()
    exc = None
    t1 = time()
    try:
        exec(
            "async def __e(client, message):\n" +
            "".join(f"\n {l}" for l in code.split("\n"))
        )
        await locals()["__e"](client, message)
    except Exception:
        exc = traceback.format_exc()
    sys.stdout, sys.stderr = old_stdout, old_stderr
    output = buf.getvalue() or exc or "Success"
    elapsed = round((time() - t1) * 1000, 2)
    result = f"<pre language='python'>{output}</pre>\n⏱ {elapsed}ms"
    if len(result) > 4096:
        with open("output.txt", "w") as f:
            f.write(output)
        await message.reply_document("output.txt")
        os.remove("output.txt")
    else:
        await message.reply_text(result)


@app.on_message(filters.command("sh") & filters.private & filters.user(OWNER_ID))
async def shell_cmd(client, message: Message):
    import subprocess
    if len(message.command) < 2:
        return await message.reply_text("Provide a shell command.")
    cmd = message.text.split(None, 1)[1]
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    output = (out or err).decode("utf-8", errors="replace").strip() or "Done."
    if len(output) > 4096:
        with open("shell_out.txt", "w") as f:
            f.write(output)
        await message.reply_document("shell_out.txt")
        os.remove("shell_out.txt")
    else:
        await message.reply_text(f"<pre>{output}</pre>")
