import importlib
import inspect
import pkgutil
from logging import getLogger
from typing import Iterator

from discord import NoEntryPointError

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
        extensions = sorted(set(ExtensionLoader._walk_extensions()))
        log.debug("Extensions set is %s", extensions)
        log.debug("Extensions count: %s", len(extensions))

        loaded = 0
        not_loaded = 0
        for extension in extensions:
            extension_name =  extension.split(".")[-1]
            try:
                bot.load_extension(extension)
                log.debug("Extension loaded: '%s'", extension_name)
                loaded += 1
            except NoEntryPointError:
                log.warning("Extension not loaded: '%s' [ Has no 'setup' function ]", extension_name)
                not_loaded += 1

        if (not_loaded < 1):
            log.info("Loaded extensions: %s | Not loaded extensions: %s", loaded, not_loaded)
        else:
            log.warning("Loaded extensions: %s | Not loaded extensions: %s", loaded, not_loaded)
