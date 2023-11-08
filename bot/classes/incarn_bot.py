from logging import getLogger

from discord import Activity, ActivityType, AllowedMentions, Bot, Intents

from ..config import CLIENT_CONFIG

log = getLogger()


class IncarnBot(Bot):

    def __init__(self) -> None:
        intents = Intents(
            members=True,
            messages=True,
            message_content=True,
            guilds=True,
            bans=True
        )

        super().__init__(
            command_prefix=CLIENT_CONFIG.prefix,
            intents=intents,
            owners_ids=CLIENT_CONFIG.owners,
            help_command=None,
            allowed_mentions=AllowedMentions.none(),
            activity=Activity(type=ActivityType.listening, name="/help")
        )

    async def on_ready(self) -> None:
        log.info("Incarn is ready.")

    def run(self) -> None:
        super().run(CLIENT_CONFIG.token)
