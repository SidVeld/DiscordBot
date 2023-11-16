import os
from dataclasses import dataclass

from dotenv import load_dotenv

from .classes.exceptions import UnconvertibleVariableError


def get_bool(env_value: str) -> bool:
    match env_value.lower():
        case "true":
            return True
        case "false":
            return False
        case _:
            message = f"Cannot convert '{env_value}' to True or False."
            raise UnconvertibleVariableError(message)


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
class DatabaseConfig:
    host: str
    port: str
    username: str
    password: str
    database: str


load_dotenv()


CLIENT_CONFIG = ClientConfig(
    os.getenv("BOT_PREFIX"),
    os.getenv("BOT_TOKEN"),
    get_list(os.getenv("BOT_OWNERS")),
    get_bool(os.getenv("BOT_SYNC_COMMANDS")),
)


DEBUG_CONFIG = DebugConfig(
    get_bool(os.getenv("DEBUG_ENABLED")),
    get_bool(os.getenv("DEBUG_ORM")),
    get_list(os.getenv("DEBUG_GUILDS"))
)


DATABASE_CONFIG = DatabaseConfig(
    os.getenv("POSTGRES_HOST"),
    os.getenv("POSTGRES_PORT"),
    os.getenv("POSTGRES_USER"),
    os.getenv("POSTGRES_PASSWORD"),
    os.getenv("POSTGRES_DB"),
)
