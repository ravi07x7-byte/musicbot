import random
from os.path import realpath
import aiohttp

THEMES = [
    "3024-night", "a11y-dark", "blackboard", "dracula-pro",
    "monokai", "nightowl", "nord", "one-dark", "synthwave-84",
    "vscode", "zenburn",
]
COLOURS = [
    "#FF5733", "#FFFF00", "#008000", "#0000FF", "#800080",
    "#FF00FF", "#00FFFF", "#30D5C8", "#4B0082", "#000000",
]


class CarbonAPI:
    def __init__(self):
        self.language = "auto"
        self.font_family = "JetBrains Mono"
        self.drop_shadow = True
        self.drop_shadow_offset = "20px"
        self.drop_shadow_blur = "68px"
        self.width_adjustment = True
        self.watermark = False

    async def generate(self, text: str, user_id) -> str:
        async with aiohttp.ClientSession(
            headers={"Content-Type": "application/json"}
        ) as ses:
            params = {
                "code": text,
                "backgroundColor": random.choice(COLOURS),
                "theme": random.choice(THEMES),
                "dropShadow": self.drop_shadow,
                "dropShadowOffsetY": self.drop_shadow_offset,
                "dropShadowBlurRadius": self.drop_shadow_blur,
                "fontFamily": self.font_family,
                "language": self.language,
                "watermark": self.watermark,
                "widthAdjustment": self.width_adjustment,
            }
            try:
                resp = await ses.post(
                    "https://carbonara.solopov.dev/api/cook", json=params
                )
                data = await resp.read()
                path = f"cache/carbon_{user_id}.jpg"
                with open(path, "wb") as f:
                    f.write(data)
                return realpath(path)
            except Exception as e:
                raise Exception(f"Carbon API error: {e}")
