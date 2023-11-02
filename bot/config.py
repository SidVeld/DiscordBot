import dacite

from dataclasses import dataclass
from pathlib import Path
from yaml import safe_load


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
    database_path: str


@dataclass
class DatabaseConfig:
    driver: str
    init: bool
    postgres_config: PostgresConfig
    sqlite_config: SqliteConfig


CONFIG_PATH = Path("config.yml")
CONFIG_DATA = safe_load(CONFIG_PATH.open("r", encoding="utf-8"))

DATABASE_CONFIG_DATA = CONFIG_DATA["database"]

CLIENT_CONFIG = dacite.from_dict(ClientConfig, CONFIG_DATA["client"])
DEBUG_CONFIG = dacite.from_dict(DebugConfig, CONFIG_DATA["debug"])
DATABASE_CONFIG = DatabaseConfig(
    DATABASE_CONFIG_DATA["driver"],
    DATABASE_CONFIG_DATA["init"],
    dacite.from_dict(PostgresConfig, DATABASE_CONFIG_DATA["postgres_config"]),
    dacite.from_dict(SqliteConfig, DATABASE_CONFIG_DATA["sqlite_config"]),
)
