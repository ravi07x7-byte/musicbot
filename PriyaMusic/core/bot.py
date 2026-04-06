from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus, ParseMode
import config
from ..logging import LOGGER


class Priya(Client):
    def __init__(self):
        LOGGER(__name__).info("Starting PriyaMusic bot...")
        super().__init__(
            name="PriyaMusic",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            parse_mode=ParseMode.HTML,
            max_concurrent_transmissions=7,
        )

    async def start(self):
        await super().start()
        self.id = self.me.id
        self.name = self.me.first_name + (" " + self.me.last_name if self.me.last_name else "")
        self.username = self.me.username
        self.mention = self.me.mention

        try:
            await self.send_message(
                chat_id=config.LOGGER_ID,
                text=(
                    f"<u><b>» {self.mention} started :</b></u>\n\n"
                    f"ID : <code>{self.id}</code>\n"
                    f"Name : {self.name}\n"
                    f"Username : @{self.username}"
                ),
            )
        except (errors.ChannelInvalid, errors.PeerIdInvalid):
            LOGGER(__name__).error(
                "Cannot access log group. Add bot as admin and check LOGGER_ID."
            )
            exit(1)
        except Exception as ex:
            LOGGER(__name__).error(f"Log group error: {type(ex).__name__}: {ex}")
            exit(1)

        member = await self.get_chat_member(config.LOGGER_ID, self.id)
        if member.status != ChatMemberStatus.ADMINISTRATOR:
            LOGGER(__name__).error("Bot must be admin in log group.")
            exit(1)

        LOGGER(__name__).info(f"PriyaMusic started as {self.name}")

    async def stop(self):
        await super().stop()
        LOGGER(__name__).info("PriyaMusic stopped.")
