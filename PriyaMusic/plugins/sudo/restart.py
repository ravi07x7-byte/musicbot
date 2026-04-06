import asyncio
import os
import shutil
import socket
from datetime import datetime

import urllib3
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
from pyrogram import filters
from pyrogram.types import Message

import config
from PriyaMusic import app
from PriyaMusic.misc import HAPP, SUDOERS, XCB
from PriyaMusic.utils.database import (
    get_active_chats,
    remove_active_chat,
    remove_active_video_chat,
)
from PriyaMusic.utils.decorators import language
from PriyaMusic.utils.pastebin import PriyaBin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _is_heroku():
    return "heroku" in socket.getfqdn()


@app.on_message(filters.command(["getlog", "logs"]) & SUDOERS)
@language
async def logs_cmd(client, message: Message, _):
    try:
        await message.reply_document("log.txt")
    except Exception:
        await message.reply_text(_["server_1"])


@app.on_message(filters.command(["update", "gitpull"]) & SUDOERS)
@language
async def update_cmd(client, message: Message, _):
    if _is_heroku() and HAPP is None:
        return await message.reply_text(_["server_2"])
    response = await message.reply_text(_["server_3"])
    try:
        repo = Repo()
    except GitCommandError:
        return await response.edit(_["server_4"])
    except InvalidGitRepositoryError:
        return await response.edit(_["server_5"])

    os.system(f"git fetch origin {config.UPSTREAM_BRANCH} &> /dev/null")
    await asyncio.sleep(7)

    REPO_ = repo.remotes.origin.url.split(".git")[0]
    commits = list(repo.iter_commits(f"HEAD..origin/{config.UPSTREAM_BRANCH}"))
    if not commits:
        return await response.edit(_["server_6"])

    def _ordinal(n):
        return f"{n}{'tsnrhtdd'[(n//10%10!=1)*(n%10<4)*n%10::4]}"

    updates = ""
    for info in commits:
        d = datetime.fromtimestamp(info.committed_date)
        updates += (
            f"<b>➣ #{info.count()}: "
            f"<a href={REPO_}/commit/{info}>{info.summary}</a> "
            f"by {info.author}</b>\n"
            f"  ➥ Committed: {_ordinal(int(d.strftime('%d')))} {d.strftime('%b, %Y')}\n\n"
        )

    full_text = f"<b>New update available!</b>\n\nPushing now...\n\n<b>Updates:</b>\n\n{updates}"
    if len(full_text) > 4096:
        url = await PriyaBin(updates)
        nrs = await response.edit(
            f"<b>New update available!</b>\n\n<a href={url}>View updates</a>"
        )
    else:
        nrs = await response.edit(full_text, disable_web_page_preview=True)

    os.system("git stash &> /dev/null && git pull")

    for cid in await get_active_chats():
        try:
            await app.send_message(int(cid), _["server_8"].format(app.mention))
            await remove_active_chat(cid)
            await remove_active_video_chat(cid)
        except Exception:
            pass

    await response.edit(f"{nrs.text}\n\n{_['server_7']}")

    if _is_heroku():
        try:
            os.system(
                f"{XCB[5]} {XCB[7]} {XCB[9]}{XCB[4]}{XCB[0]*2}{XCB[6]}{XCB[4]}"
                f"{XCB[8]}{XCB[1]}{XCB[5]}{XCB[2]}{XCB[6]}{XCB[2]}{XCB[3]}"
                f"{XCB[0]}{XCB[10]}{XCB[2]}{XCB[5]} {XCB[11]}{XCB[4]}{XCB[12]}"
            )
        except Exception as err:
            await response.edit(f"{nrs.text}\n\n{_['server_9']}")
            await app.send_message(config.LOGGER_ID, _["server_10"].format(err))
    else:
        os.system("pip3 install -r requirements.txt")
        os.system(f"kill -9 {os.getpid()} && bash start")
        exit()


@app.on_message(filters.command("restart") & SUDOERS)
async def restart_cmd(_, message: Message):
    response = await message.reply_text("Restarting...")
    for cid in await get_active_chats():
        try:
            await app.send_message(
                int(cid),
                f"{app.mention} is restarting. Please wait ~20 seconds.",
            )
            await remove_active_chat(cid)
            await remove_active_video_chat(cid)
        except Exception:
            pass
    for folder in ("downloads", "raw_files", "cache"):
        try:
            shutil.rmtree(folder)
        except Exception:
            pass
    await response.edit_text("✅ Restart initiated. Back in ~20 seconds.")
    os.system(f"kill -9 {os.getpid()} && bash start")
