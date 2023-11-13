from logging import getLogger

from discord import Activity, ActivityType, AllowedMentions, Bot, Intents
from tortoise import Tortoise

from ..config import CLIENT_CONFIG, DATABASE_CONFIG

log = getLogger(__name__)


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

    async def setup_database(self) -> None:
        username = DATABASE_CONFIG.username
        password = DATABASE_CONFIG.password
        host = DATABASE_CONFIG.host
        port = DATABASE_CONFIG.port
        database = DATABASE_CONFIG.database
        await Tortoise.init(
            db_url=f"postgres://{username}:{password}@{host}:{port}/{database}",
            modules={"models": ["bot.models"]}
        )
        await Tortoise.generate_schemas()

    async def start(self, token: str, *, reconnect: bool = True) -> None:
        await self.setup_database()
        await super().start(token, reconnect=reconnect)

    async def close(self) -> None:
        await Tortoise.close_connections()
        await super().close()

    async def on_ready(self) -> None:
        log.info("Incarn is ready.")

    def run(self) -> None:
        super().run(CLIENT_CONFIG.token)
