import platform
from logging import getLogger

import discord
from discord import ApplicationContext as AppCtx
from discord import Bot, Embed, slash_command

from bot.classes.extension import Extension

log = getLogger()


class Information(Extension):
    @slash_command(name="ping", description="Sends bot's latency")
    async def ping_command(self, ctx: AppCtx) -> None:
        latency = round(self.bot.latency * 1000)
        log.debug("Gateway Latency: %s ms", latency)
        ping_embed = Embed(
            title="Pong!",
            description=f"Gateway Latency: {latency}ms"
        )
        await ctx.respond(embed=ping_embed)

    @slash_command(name="revision", description="Sends bot's revision")
    async def revision_command(self, ctx: AppCtx) -> None:
        embed = Embed(title="Revision")
        embed.add_field(name="Pycord", value=discord.__version__)
        embed.add_field(name="Python", value=platform.python_version())

        await ctx.respond(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Information(bot))
