import random
from logging import getLogger

from discord import ApplicationContext as AppCtx
from discord import Bot, Embed, SlashCommandGroup, option

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

    def __get_rolls_string(self, rolls: list[int], sort: bool = False) -> str:
        if sort:
            return " - ".join(str(roll) for roll in sorted(rolls))
        return " - ".join(str(roll) for roll in rolls)

    def __get_roll_result_string(self, rolls: list[int]) -> str:
        return MESSAGE_TEMPLATE.format(
            self.__get_rolls_string(rolls),
            self.__get_rolls_string(rolls, True)
        )

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
        min_value=0,
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
        rolls = [random.randint(1, 10) for _ in range(amount + mod - wound_penalty)]
        result = 0
        added_rolls = 0

        for roll in rolls:
            if special and roll == 10:
                result += 1
                added_rolls += 1
                rolls.append(random.randint(1, 10))
                continue

            if roll >= difficulty:
                result += 1
                continue

            if roll == 1:
                result -= 1
                continue

        if result > 0:
            embed_title = "Success!"
            embed_color = RollResultColors.SUCCESS
        elif result == 0:
            embed_title = "Unsuccessfully!"
            embed_color = RollResultColors.UNSUCCESSFUL
        else:
            embed_title = "Failure!"
            embed_color = RollResultColors.FAILURE
        embed_description = self.__get_roll_result_string(rolls)

        embed = Embed(
            title=embed_title,
            description=embed_description,
            color=embed_color
        )

        embed.add_field(name="Amount", value=str(amount))
        embed.add_field(name="Difficulty", value=str(difficulty))
        embed.add_field(name="Modifiers", value=str(mod))
        embed.add_field(name="Wounds", value="None" if wound_name == "None" else wounds)
        embed.add_field(name="Is special?", value=f"Yes (added {added_rolls})" if special else "No")
        embed.add_field(name="Result", value=f"{result} Successes")

        log.debug(
            "VTM: '%s' | A: %s | %s | D: %s | M: %s | W: %s | S: %s | R: %s",
            ctx.author.name,
            amount,
            rolls,
            difficulty,
            mod,
            wound_penalty,
            special,
            result
        )

        await ctx.respond(embed=embed)

    @vtm.command(name="soak", description="Calculates the amount of absorbed damage.")
    @option("damage", description="How much damage should the character be dealt?", min_value=1)
    @option("stamina", description="How much stamina does the character have?", min_value=0, max_value=10)
    @option("armor", description="What is the character's armor rating?", default=0, min_value=0)
    @option("mod", description="What will be the modifier?", default=0)
    async def vtm_soak(self, ctx: AppCtx, damage: int, stamina: int, *, armor: int, mod: int) -> None:
        rolls = [random.randint(1, 10) for _ in range(stamina + armor + mod)]

        difficult = 6
        absorbed_damage = 0
        for roll in rolls:
            if roll >= difficult:
                absorbed_damage += 1

        final_damage = max(damage - absorbed_damage, 0)

        if final_damage > 0:
            embed_title = f"{final_damage} damage done!"
            embed_color = RollResultColors.FAILURE
        else:
            embed_title = "All damage absorbed!"
            embed_color = RollResultColors.SUCCESS
        embed_description = self.__get_roll_result_string(rolls)

        embed = Embed(title=embed_title, description=embed_description, color=embed_color)
        embed.add_field(name="Stamina", value=str(stamina))
        embed.add_field(name="Armor", value=str(armor))
        embed.add_field(name="Modifiers", value=str(mod))
        embed.add_field(name="Damage", value=str(damage))
        embed.add_field(name="Absorbed", value=str(absorbed_damage))
        embed.add_field(name="Final damage", value=str(final_damage))
        await ctx.respond(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(VTM(bot))
