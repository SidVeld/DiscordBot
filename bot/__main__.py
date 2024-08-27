from logging import getLogger

from .classes.edgar_bot import EdgarBot
from .utils import ExtensionLoader

log = getLogger(__name__)

try:
    bot = EdgarBot()
    ExtensionLoader.load_extensions(bot)
    bot.run()

except Exception as error:
    log.fatal("Unknown startup error occurred!")
    log.fatal(error)
    exit(69)
