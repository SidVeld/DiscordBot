import tortoise

from logging import getLogger
from tortoise import Tortoise
from enum import Enum

from ..config import DATABASE_CONFIG
from ..classes.errors import UnsupportedDatabaseError


log = getLogger()


MODELS_PACKAGE = "bot.models"


class DatabaseDrivers(Enum):
    POSTGRES = "postgres"
    SQLITE = "sqlite"


class DatabaseController:

    @staticmethod
    async def __init__postgres() -> None:
        username = DATABASE_CONFIG.username
        password = DATABASE_CONFIG.password
        host = DATABASE_CONFIG.host
        port = DATABASE_CONFIG.port
        database = DATABASE_CONFIG.database
        await Tortoise.init(
            db_url=f"postgres://{username}:{password}@{host}:{port}/{database}",
            modules={"models": [MODELS_PACKAGE]}
        )

    @staticmethod
    async def __init_sqlite() -> None:
        await Tortoise.init(
            db_url=f"sqlite://{DATABASE_CONFIG.sqlite_path}",
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
                log.warning(f"Unsupported database driver: {DATABASE_CONFIG.driver.lower()}")
                raise UnsupportedDatabaseError()

        await Tortoise.generate_schemas()

        log.info("Database setup finished")

    @staticmethod
    def setup_database() -> None:
        tortoise.run_async(DatabaseController.__run_database_init())
