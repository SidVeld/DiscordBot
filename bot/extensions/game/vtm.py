import random

from logging import getLogger

from discord import ApplicationContext as AppCtx, Embed, Bot, option, SlashCommandGroup

from bot.classes.extension import Extension


log = getLogger()


class VTM(Extension):

    vtm = SlashCommandGroup("vtm", "Commands for Vampire The Masquerade")

    @vtm.command(name="roll", description="Rolls the dices.")
    @option(name="amount", description="Amount of dices.", min_value=1, max_value=15)
    @option(name="difficulty", description="Success threshold.", min_value=1, max_value=10)
    @option(name="mod", description="Bonus dices.", min_value=1)
    @option(name="special", description="Is this roll should explode tens?")
    async def vtm_roll(self, ctx: AppCtx, amount: int, difficulty: int, mod: int = 0, special: bool = False) -> None:
        dices = [random.randint(1, 10) for _ in range(amount + mod)]
        result = 0

        for dice in dices:
            if special and dice == 10:
                result += 1
                dices.append(random.randint(1, 10))
                continue

            if dice >= difficulty:
                result += 1
                continue

            if dice == 1:
                result -= 1
                continue

        if result > 0:
            title = "Success!"
            color = 0xa7c957
        elif result == 0:
            title = "Unsuccessfully!"
            color = 0xf2e8cf
        else:
            title = "Failure!"
            color = 0xbc4749

        log.debug(f"{dices} : {result} -> {title}")

        embed = Embed(
            title=title,
            description=" ".join(str(die) for die in dices),
            color=color
        )

        embed.add_field(name="Result", value=f"{result} Successes")
        embed.add_field(name="Is special?", value=special)

        await ctx.respond(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(VTM(bot))
