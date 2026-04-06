import os
from config import autoclean


async def auto_clean(popped: dict):
    try:
        rem = popped.get("file", "")
        if rem in autoclean:
            autoclean.remove(rem)
        if autoclean.count(rem) == 0:
            # Only delete local downloads, not streaming URLs
            if all(tag not in rem for tag in ("vid_", "live_", "index_")):
                if os.path.isfile(rem):
                    try:
                        os.remove(rem)
                    except Exception:
                        pass
    except Exception:
        pass
