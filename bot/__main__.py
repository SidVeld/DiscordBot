from logging import getLogger

from .classes.incarn_bot import IncarnBot
from .utils import ExtensionLoader

log = getLogger(__name__)

try:
    bot = IncarnBot()
    ExtensionLoader.load_extensions(bot)
    bot.run()

except Exception as error:
    log.fatal("Unknown startup error occurred!")
    log.fatal(error)
    exit(69)
