import time
import psutil
from PriyaMusic.misc import _boot_
from PriyaMusic.utils.formatters import get_readable_time


async def bot_sys_stats():
    uptime = int(time.time() - _boot_)
    UP = get_readable_time(uptime)
    CPU = f"{psutil.cpu_percent(interval=0.5)}%"
    RAM = f"{psutil.virtual_memory().percent}%"
    DISK = f"{psutil.disk_usage('/').percent}%"
    return UP, CPU, RAM, DISK
