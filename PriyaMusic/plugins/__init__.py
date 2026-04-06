import glob
from os.path import dirname, isfile


def _list_modules():
    base = dirname(__file__)
    paths = glob.glob(base + "/*/*.py")
    modules = [
        (f.replace(base, "").replace("/", ".")[:-3])
        for f in paths
        if isfile(f) and not f.endswith("__init__.py")
    ]
    return sorted(modules)


ALL_MODULES = _list_modules()
__all__ = ALL_MODULES + ["ALL_MODULES"]
