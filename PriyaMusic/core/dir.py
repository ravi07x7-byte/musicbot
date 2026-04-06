import os
from ..logging import LOGGER


def dirr():
    for fname in os.listdir("."):
        if fname.endswith((".jpg", ".jpeg", ".png")):
            try:
                os.remove(fname)
            except OSError:
                pass

    for folder in ("downloads", "cache"):
        if folder not in os.listdir("."):
            os.makedirs(folder, exist_ok=True)

    LOGGER(__name__).info("Directories ready.")
