import os
from dataclasses import dataclass

from dotenv import load_dotenv

from .classes.errors import ConfigWrongBoolValueError


def get_bool(env_value: str) -> bool:
    env_value = env_value.lower()
    match env_value:
        case "true":
            return True
        case "false":
            return False
        case _:
            raise ConfigWrongBoolValueError()


def get_list(env_value: str) -> list:
    return [item for item in env_value.split(",")]


@dataclass
class ClientConfig:
    prefix: str
    token: str
    owners: list[int]
    sync_commands: bool


@dataclass
class DebugConfig:
    enabled: bool
    debug_orm: bool
    guilds: list[int]


@dataclass
class PostgresConfig:
    host: str
    port: int
    username: str
    password: str
    database: str


@dataclass
class SqliteConfig:
    database: str


@dataclass
class DatabaseConfig:
    driver: str
    init: bool
    postgres_config: PostgresConfig
    sqlite_config: SqliteConfig


load_dotenv()


CLIENT_CONFIG = ClientConfig(
    os.getenv("BOT_PREFIX"),
    os.getenv("BOT_TOKEN"),
    get_list(os.getenv("BOT_OWNERS")),
    get_bool(os.getenv("BOT_SYNC_COMMANDS"))
)


DEBUG_CONFIG = DebugConfig(
    get_bool(os.getenv("DEBUG_ENABLED")),
    get_bool(os.getenv("DEBUG_ORM")),
    get_list(os.getenv("DEBUG_GUILDS"))
)


DATABASE_CONFIG = DatabaseConfig(
    os.getenv("DATABASE_DRIVER"),
    get_bool(os.getenv("DATABASE_INIT")),
    PostgresConfig(
        os.getenv("POSTGRES_HOST"),
        os.getenv("POSTGRES_PORT"),
        os.getenv("POSTGRES_USERNAME"),
        os.getenv("POSTGRES_PASSWORD"),
        os.getenv("POSTGRES_DATABASE")
    ),
    SqliteConfig(os.getenv("SQLITE_DATABASE"))
)
