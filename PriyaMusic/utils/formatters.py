import json
import subprocess
from typing import Tuple


def get_readable_time(seconds: int) -> str:
    count = 0
    time_list = []
    suffixes = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(f"{int(result)}{suffixes[count-1]}")
        seconds = int(remainder)
    if len(time_list) == 4:
        prefix = time_list.pop() + ", "
    else:
        prefix = ""
    time_list.reverse()
    return prefix + ":".join(time_list)


def convert_bytes(size: float) -> str:
    if not size:
        return ""
    power = 1024
    n = 0
    labels = {0: " ", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {labels[n]}B"


async def int_to_alpha(user_id: int) -> str:
    alpha = "abcdefghij"
    return "".join(alpha[int(d)] for d in str(user_id))


async def alpha_to_int(s: str) -> int:
    alpha = "abcdefghij"
    return int("".join(str(alpha.index(c)) for c in s))


def time_to_seconds(time: str) -> int:
    parts = str(time).split(":")
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(parts)))


def seconds_to_min(seconds) -> str:
    if seconds is None:
        return "-"
    s = int(seconds)
    d, h, m, sec = s // 86400, s // 3600 % 24, s % 3600 // 60, s % 60
    if d > 0:
        return f"{d:02d}:{h:02d}:{m:02d}:{sec:02d}"
    elif h > 0:
        return f"{h:02d}:{m:02d}:{sec:02d}"
    elif m > 0:
        return f"{m:02d}:{sec:02d}"
    elif sec > 0:
        return f"00:{sec:02d}"
    return "-"


def speed_converter(seconds, speed: float) -> Tuple[str, float]:
    factors = {0.5: 2.0, 0.75: 1.5, 1.5: 0.75, 2.0: 0.5}
    factor = factors.get(speed, 1.0)
    new_sec = seconds * factor
    return seconds_to_min(int(new_sec)), new_sec


def check_duration(file_path: str) -> float:
    cmd = [
        "ffprobe", "-loglevel", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        file_path,
    ]
    pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, _ = pipe.communicate()
    try:
        data = json.loads(out)
    except Exception:
        return 0
    if "format" in data and "duration" in data["format"]:
        return float(data["format"]["duration"])
    for s in data.get("streams", []):
        if "duration" in s:
            return float(s["duration"])
    return 0


VIDEO_FORMATS = [
    "webm", "mkv", "flv", "vob", "ogv", "ogg", "mov", "avi", "wmv",
    "mp4", "m4p", "m4v", "mpg", "mpeg", "mpe", "3gp", "3g2", "f4v",
]
