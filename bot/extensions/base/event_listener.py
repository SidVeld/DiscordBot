from discord import Cog, Bot
from discord.ext.commands import Context

from bot.classes.extension import Extension
from bot.models import UserModel

from logging import getLogger


log = getLogger()


class EventListener(Extension):

    @Cog.listener()
    async def on_application_command(self, ctx: Context) -> None:
        author = ctx.author

        if user := await UserModel.get_or_none(discord_id=author.id):
            if user.username == author.name:
                return
            await UserModel.update_from_dict(username=author.name)
        else:
            await UserModel.create(discord_id=author.id, username=author.name)


def setup(bot: Bot) -> None:
    bot.add_cog(EventListener(bot))
