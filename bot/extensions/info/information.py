from logging import getLogger

from discord import ApplicationContext as AppCtx, slash_command, Embed, Bot

from bot.classes.extension import Extension


log = getLogger()


class Information(Extension):
    @slash_command(name="ping", description="Sends the bot's latency")
    async def ping_command(self, ctx: AppCtx):
        latency = round(self.bot.latency * 1000)
        log.debug(f"Gateway Latency: {latency}ms")
        ping_embed = Embed(
            title="Pong!",
            description=f"Gateway Latency: {latency}ms"
        )
        await ctx.respond(embed=ping_embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Information(bot))
