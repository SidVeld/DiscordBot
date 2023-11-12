from logging import getLogger

from discord import Bot, Cog
from discord.ext.commands import Context

from bot.classes.extension import Extension
from bot.models import UserModel

log = getLogger(__name__)


class EventListener(Extension):

    @Cog.listener()
    async def on_application_command(self, ctx: Context) -> None:
        author = ctx.author

        if user := await UserModel.get_or_none(user_id=author.id):
            if user.username == author.name:
                return

            log.info(
                "Updating the user name in the database: '%s' -> '%s' (%s)",
                user.username,
                author.name,
                user.user_id,
            )

            user.username = author.name
            await user.save()
        else:
            log.info("Registering a new user in the database: '%s' (%s)", author.name, author.id)
            await UserModel.create(user_id=author.id, username=author.name)


def setup(bot: Bot) -> None:
    bot.add_cog(EventListener(bot))
