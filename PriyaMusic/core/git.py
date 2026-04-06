import asyncio
import shlex
from typing import Tuple

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError

import config
from ..logging import LOGGER


def _run(cmd: str) -> Tuple[str, str, int, int]:
    async def _inner():
        args = shlex.split(cmd)
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, err = await proc.communicate()
        return out.decode("utf-8", "replace").strip(), err.decode("utf-8", "replace").strip(), proc.returncode, proc.pid
    return asyncio.get_event_loop().run_until_complete(_inner())


def git():
    repo_url = config.UPSTREAM_REPO
    if config.GIT_TOKEN:
        user = repo_url.split("com/")[1].split("/")[0]
        host = repo_url.split("https://")[1]
        repo_url = f"https://{user}:{config.GIT_TOKEN}@{host}"

    try:
        Repo()
        LOGGER(__name__).info("Git repo found (VPS mode).")
        return
    except GitCommandError:
        LOGGER(__name__).info("Invalid git command.")
        return
    except InvalidGitRepositoryError:
        pass

    repo = Repo.init()
    origin = (
        repo.remote("origin")
        if "origin" in repo.remotes
        else repo.create_remote("origin", repo_url)
    )
    origin.fetch()
    branch = config.UPSTREAM_BRANCH
    repo.create_head(branch, origin.refs[branch])
    repo.heads[branch].set_tracking_branch(origin.refs[branch])
    repo.heads[branch].checkout(True)
    try:
        repo.create_remote("origin", config.UPSTREAM_REPO)
    except Exception:
        pass
    nrs = repo.remote("origin")
    nrs.fetch(branch)
    try:
        nrs.pull(branch)
    except GitCommandError:
        repo.git.reset("--hard", "FETCH_HEAD")
    _run("pip3 install --no-cache-dir -r requirements.txt")
    LOGGER(__name__).info("Pulled updates from upstream.")
