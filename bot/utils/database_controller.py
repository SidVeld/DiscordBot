from enum import Enum
from logging import getLogger

import tortoise
from tortoise import Tortoise

from ..classes.errors import UnsupportedDatabaseError
from ..config import DATABASE_CONFIG

log = getLogger()


MODELS_PACKAGE = "bot.models"


class DatabaseDrivers(Enum):
    POSTGRES = "postgres"
    SQLITE = "sqlite"


class DatabaseController:

    @staticmethod
    async def __init__postgres() -> None:
        config = DATABASE_CONFIG.postgres_config
        username = config.username
        password = config.password
        host = config.host
        port = config.port
        database = config.database
        await Tortoise.init(
            db_url=f"postgres://{username}:{password}@{host}:{port}/{database}",
            modules={"models": [MODELS_PACKAGE]}
        )

    @staticmethod
    async def __init_sqlite() -> None:
        config = DATABASE_CONFIG.sqlite_config
        await Tortoise.init(
            db_url=f"sqlite://{config.database_path}",
            modules={"models": [MODELS_PACKAGE]}
        )

    @staticmethod
    async def __run_database_init() -> None:
        log.info("Database setup started")

        match DATABASE_CONFIG.driver.lower():
            case DatabaseDrivers.POSTGRES.value:
                log.debug("Using postgres database driver")
                await DatabaseController.__init__postgres()
            case DatabaseDrivers.SQLITE.value:
                log.debug("Using sqlite database driver")
                await DatabaseController.__init_sqlite()
            case _:
                log.warning("Unsupported database driver: %s", DATABASE_CONFIG.driver.lower())
                raise UnsupportedDatabaseError()

        await Tortoise.generate_schemas()

        log.info("Database setup finished")

    @staticmethod
    def init_database() -> None:
        if not DATABASE_CONFIG.init:
            log.debug("Database init is False. Skipping initialization")
            return
        tortoise.run_async(DatabaseController.__run_database_init())
