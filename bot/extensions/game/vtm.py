import random
from logging import getLogger

from discord import ApplicationContext as AppCtx, Embed, Bot, option, SlashCommandGroup

from bot.classes.extension import Extension

from ._roll_colors import RollResultColors


log = getLogger()


MESSAGE_TEMPLATE = """
**Rolls**
{0}

**Sorted**
{1}
"""


WOUNDS = {
    "None": 0,
    "Bruised": 0,
    "Hurt": 1,
    "Injured": 1,
    "Wounded": 2,
    "Mauled": 2,
    "Crippled": 5
}


WOUNDS_NAMES = [f"{name} (-{penalty})" for name, penalty in WOUNDS.items()]


class VTM(Extension):
    vtm = SlashCommandGroup("vtm", "Commands for Vampire The Masquerade")

    @vtm.command(name="roll", description="Rolls the dices.")
    @option(
        name="amount",
        description="Amount of dices.",
        min_value=1,
        max_value=15
    )
    @option(
        name="difficulty",
        description="Success threshold.",
        min_value=1,
        max_value=10
    )
    @option(
        name="mod",
        description="Bonus dices.",
        min_value=1,
        max_value=10
    )
    @option(
        name="wounds",
        description="What are the character's wounds right now? Affects the number of dice.",
        choices=WOUNDS_NAMES
    )
    @option(
        name="special",
        description="Is this roll should explode tens?"
    )
    async def vtm_roll(
        self,
        ctx: AppCtx,
        amount: int,
        difficulty: int = 6,
        mod: int = 0,
        wounds: str = "None",
        special: bool = False
    ) -> None:
        wound_name = wounds.split(" ")[0]
        wound_penalty = WOUNDS[wound_name]
        dices = [random.randint(1, 10) for _ in range(amount + mod - wound_penalty)]
        result = 0
        add_rolls = 0

        for dice in dices:
            if special and dice == 10:
                result += 1
                add_rolls += 1
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
            color = RollResultColors.SUCCESS.value
        elif result == 0:
            title = "Unsuccessfully!"
            color = RollResultColors.UNSUCCESSFUL.value
        else:
            title = "Failure!"
            color = RollResultColors.FAILURE.value

        log.debug(
            "VTM: '{}' | A: {} | {} | D: {} | M: {} | W: {} | S: {} | R: {}".format(
                ctx.author.name,
                amount,
                dices,
                difficulty,
                mod,
                wound_penalty,
                special,
                result
            )
        )

        description = MESSAGE_TEMPLATE.format(
            " - ".join(str(die) for die in dices),
            " - ".join(str(die) for die in sorted(dices))
        )

        embed = Embed(
            title=title,
            description=description,
            color=color
        )

        embed.add_field(name="Amount", value=str(amount))
        embed.add_field(name="Difficulty", value=str(difficulty))
        embed.add_field(name="Modifiers", value=str(mod))
        embed.add_field(name="Wounds", value=wounds)
        embed.add_field(name="Is special?", value=f"Yes (added {add_rolls})" if special else "No")
        embed.add_field(name="Result", value=f"{result} Successes")

        await ctx.respond(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(VTM(bot))
