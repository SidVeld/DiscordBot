import importlib
import inspect
import pkgutil
from logging import getLogger
from typing import Iterator

from .. import extensions
from ..classes.incarn_bot import IncarnBot

log = getLogger()


class ExtensionLoader:
    @staticmethod
    def _get_unqualified_name(name: str) -> str:
        return name.rsplit(".", maxsplit=1)[-1]

    @staticmethod
    def _walk_extensions() -> Iterator[str]:

        def on_error(name: str) -> None:
            raise ImportError(name=name)

        for module in pkgutil.walk_packages(extensions.__path__, f"{extensions.__name__}.", onerror=on_error):
            if ExtensionLoader._get_unqualified_name(module.name).startswith("_"):
                continue

            if module.ispkg:
                imported = importlib.import_module(module.name)
                if not inspect.isfunction(getattr(imported, "setup", None)):
                    continue

            yield module.name

    @staticmethod
    def load_extensions(bot: IncarnBot) -> None:
        extensions_set = set(ExtensionLoader._walk_extensions())
        log.debug("Extension set is %s", extensions_set)

        for extension in extensions_set:
            bot.load_extension(extension)
