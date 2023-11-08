from logging import getLogger

from .classes.errors import DatabaseError, UnsupportedDatabaseError
from .classes.incarn_bot import IncarnBot
from .utils import DatabaseController, ExtensionLoader

log = getLogger()

try:
    DatabaseController.init_database()
    bot = IncarnBot()
    ExtensionLoader.load_extensions(bot)
    bot.run()

except DatabaseError as database_error:

    if isinstance(database_error, UnsupportedDatabaseError):
        log.fatal("Using wrong database driver. Check configuration file.")
        exit(1001)

except Exception as error:
    log.fatal("Unknown startup error occurred!")
    log.fatal(error)
    exit(69)
