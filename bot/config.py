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
    guilds: list[int]


@dataclass
class DatabaseConfig:
    driver: str
    host: str
    port: int
    username: str
    password: str
    database: str
    sqlite_path: str


CONFIG_PATH = Path("config.yml")
CONFIG_DATA = safe_load(CONFIG_PATH.open("r", encoding="utf-8"))


CLIENT_CONFIG = dacite.from_dict(ClientConfig, CONFIG_DATA["client"])
DEBUG_CONFIG = dacite.from_dict(DebugConfig, CONFIG_DATA["debug"])
DATABASE_CONFIG = dacite.from_dict(DatabaseConfig, CONFIG_DATA["database"])
