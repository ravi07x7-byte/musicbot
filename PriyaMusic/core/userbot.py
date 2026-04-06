from pyrogram import Client
import config
from ..logging import LOGGER

assistants: list = []
assistantids: list = []

_STRINGS = [
    config.STRING_SESSION,
    config.STRING2,
    config.STRING3,
    config.STRING4,
    config.STRING5,
]
_NAMES = ["PriyaAss1", "PriyaAss2", "PriyaAss3", "PriyaAss4", "PriyaAss5"]


class Userbot:
    def __init__(self):
        self._clients: list[Client] = []
        for i, (string, name) in enumerate(zip(_STRINGS, _NAMES), start=1):
            if string:
                client = Client(
                    name=name,
                    api_id=config.API_ID,
                    api_hash=config.API_HASH,
                    session_string=string,
                    no_updates=True,
                )
                self._clients.append((i, client))

    async def start(self):
        LOGGER(__name__).info("Starting assistant accounts...")
        for num, client in self._clients:
            await client.start()
            for ch in ("yourchannel", "yoursupport"):
                try:
                    await client.join_chat(ch)
                except Exception:
                    pass
            try:
                await client.send_message(config.LOGGER_ID, f"Assistant {num} started.")
            except Exception:
                LOGGER(__name__).error(f"Assistant {num} cannot reach log group!")
                exit(1)
            client.id = client.me.id
            client.name = client.me.mention
            client.username = client.me.username
            assistants.append(num)
            assistantids.append(client.id)
            LOGGER(__name__).info(f"Assistant {num} started as {client.name}")

    async def stop(self):
        for _, client in self._clients:
            try:
                await client.stop()
            except Exception:
                pass
        LOGGER(__name__).info("All assistants stopped.")

    async def get_client(self, num: int) -> Client | None:
        for n, c in self._clients:
            if n == num:
                return c
        return None
