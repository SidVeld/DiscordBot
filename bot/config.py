import os
from dataclasses import dataclass

from dotenv import load_dotenv

from .classes.exceptions import InconvertibleVariableError, NoneTypeVariableError


def get_env_value(env_name: str) -> str:
    env_value = os.getenv(env_name)

    if env_value is None:
        message = f"Variable `{env_name}` is None."
        raise NoneTypeVariableError(message)

    return env_value


def to_bool(env_value: str) -> bool:
    """
    Converts the type of the received environment variable to bool.

    The variable must be either `True` or `False`.
    Otherwise, an error will appear.

    :param str env_value: The value of the environment variable to be converted. Case-insensitive.
    :return: Value of environment variable of `bool` type.
    :raises InconvertibleVariableError: A variable cannot be converted to a `bool`.
    """
    match env_value.lower():
        case "true":
            return True
        case "false":
            return False
        case _:
            message = f"Cannot convert '{env_value}' to True or False."
            raise InconvertibleVariableError(message)


def to_list_int(env_value: str) -> list[int]:
    """
    Converts the type of the received environment variable to list of integers.

    :param str env_value: The value of the environment variable to be converted.
    :return: Value of environment variable of `list` type.
    """
    return [int(item.strip()) for item in env_value.split(",")]


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
    get_env_value("BOT_PREFIX"),
    get_env_value("BOT_TOKEN"),
    to_list_int(get_env_value("BOT_OWNERS")),
    to_bool(get_env_value("BOT_SYNC_COMMANDS")),
)


DEBUG_CONFIG = DebugConfig(
    to_bool(get_env_value("DEBUG_ENABLED")),
    to_bool(get_env_value("DEBUG_ORM")),
    to_list_int(get_env_value("DEBUG_GUILDS"))
)


DATABASE_CONFIG = DatabaseConfig(
    get_env_value("POSTGRES_HOST"),
    get_env_value("POSTGRES_PORT"),
    get_env_value("POSTGRES_USER"),
    get_env_value("POSTGRES_PASSWORD"),
    get_env_value("POSTGRES_DB"),
)
