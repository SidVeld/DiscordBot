import random
from discord import slash_command, ApplicationContext as AppCtx, option, Embed
from bot.classes.extension import Extension
from bot.classes.incarn_bot import IncarnBot

class Roll(Extension):

    def _get_successes(self, dices: list[int], target: int, failures: int) -> tuple[int, int]:
        successes = 0
        failures = 0

        for die in dices:
            if die >= target:
                successes += 1
                continue
            elif die <= failures:
                failures += 1
                continue

        return successes, failures

    @slash_command(name="roll", description="Roll the dice!")
    @option("amount", description="Amount of dices to roll.", min_value=1, max_value=15)
    @option("sides", description = "Amount of dice's sides.", min_value=1, max_value=1000)
    @option("target", description="Success thresshold", min_value=1)
    @option("failures", description="Failure thresshold", min_value=1)
    async def roll(
        self,
        ctx: AppCtx,
        amount: int,
        sides: int,
        target: int = 0,
        failures: int = 0
    ) -> None:
        dices = [random.randint(1, sides) for _ in range(amount)]
 
        result_embed = Embed(
            title = f"Result",
            description=" ".join(str(dice) for dice in dices)
        )

        if target:
            successes, failures = self._get_successes(dices, target, failures)

            result_embed.add_field(name="Successes", value=str(successes))
            result_embed.add_field(name="Failures", value=str(failures))
            result_embed.add_field(name="Total", value=str(successes - failures))

        result_embed.add_field(name="Sum", value=str(sum(dices))) 

        await ctx.respond(embed=result_embed)


def setup(bot: IncarnBot) -> None:
    bot.add_cog(Roll(bot))

