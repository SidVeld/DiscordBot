import random

from discord import ApplicationContext as AppCtx
from discord import Embed, SlashCommandGroup, option

from bot.classes.extension import Extension
from bot.classes.incarn_bot import IncarnBot

from ._roll_colors import RollResultColors


class DarkHeresy(Extension):
    dark_heresy = SlashCommandGroup("dark_heresy", "Commands for dark heresy!")

    @dark_heresy.command(name="roll")
    @option("target", description="Roll target.")
    @option("mod", description="Roll result modification.", min_value=-60, max_value=60)
    async def dh_roll(self, ctx: AppCtx, target: int, mod: int = 0) -> None:
        roll = random.randint(1, 100)

        if roll <= target + mod:
            result = "Success"
            color = RollResultColors.SUCCESS.value
        else:
            result = "Failure"
            color = RollResultColors.FAILURE.value

        if roll == 1 or roll == 100:
            result = f"Critical {result.lower()}"

        embed = Embed(title=result, color=color)
        embed.add_field(name="Roll", value=str(roll))
        embed.add_field(name="Target", value=str(target))

        if mod:
            embed.add_field(name="Mod", value=str(mod))

        await ctx.respond(embed=embed)


def setup(bot: IncarnBot) -> None:
    bot.add_cog(DarkHeresy(bot))

