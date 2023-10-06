import logging
from logging import FileHandler, Formatter

from pathlib import Path

from rich.logging import RichHandler

from ..config import DEBUG_CONFIG


DATE_FORMAT = "[%x | %X]"
RICH_FORMAT = "%(message)s"
FILE_FORMAT = "%(asctime)s :: %(levelname)s :: %(message)s"


def setup_logger() -> None:
    rich_handler = RichHandler(rich_tracebacks=True)
    rich_handler.setFormatter(Formatter(RICH_FORMAT, datefmt=DATE_FORMAT))

    log_file = Path("logs", "bot.log")
    log_file.parent.mkdir(exist_ok=True)

    file_handler = FileHandler(filename=log_file, encoding="utf-8", mode="a")
    file_handler.setFormatter(Formatter(FILE_FORMAT, datefmt=DATE_FORMAT))

    logging.basicConfig(
        level=logging.DEBUG if DEBUG_CONFIG.enabled else logging.INFO,
        datefmt=DATE_FORMAT,
        handlers=[rich_handler, file_handler]
    )

    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
