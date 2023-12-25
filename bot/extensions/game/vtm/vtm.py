import random
from logging import getLogger

from discord import ApplicationContext as AppCtx
from discord import Bot, Embed, SlashCommandGroup, option

from bot.classes.extension import Extension

from ._colors import VTMColors
from ._health_status import HealthStatus

log = getLogger(__name__)

ROLL_RESULT_TEMPLATE = """
**Rolls**
{0}
**Sorted**
{1}
"""

HEALTH_STATUSES = {
    0: HealthStatus("Healthy", 0),
    1: HealthStatus("Bruised", 0),
    2: HealthStatus("Hurt", 1),
    3: HealthStatus("Injured", 1),
    4: HealthStatus("Wounded", 2),
    5: HealthStatus("Mauled", 2),
    6: HealthStatus("Crippled", 5),
    7: HealthStatus("Incapacitated", 100),
}

WOUNDS_OPTIONS = [number for number in range(8)]


class VTM(Extension):
    def __get_rolls_string(self, rolls: list[int], sort: bool = False) -> str:
        if sort:
            return " - ".join(str(roll) for roll in sorted(rolls))
        return " - ".join(str(roll) for roll in rolls)

    def __get_roll_result_string(self, rolls: list[int]) -> str:
        return ROLL_RESULT_TEMPLATE.format(self.__get_rolls_string(rolls), self.__get_rolls_string(rolls, True))

    vtm = SlashCommandGroup("vtm", "Commands for Vampire The Masquerade")

    @vtm.command(name="roll", description="Rolls the dices.")
    @option("amount", description="Amount of dices.", min_value=1, max_value=15)
    @option("difficulty", description="Success threshold.", min_value=1, max_value=10, default=6)
    @option("mod", description="Bonus dices.", min_value=0, max_value=10, default=0)
    @option("wounds", int, description="Amount of character wounds", choices=WOUNDS_OPTIONS, default=0)
    @option("special", description="Is this roll should explode tens?", default=False)
    async def vtm_roll(self, ctx: AppCtx, amount: int, difficulty: int, mod: int, wounds: int, special: bool) -> None:
        health_status = HEALTH_STATUSES[wounds]

        if wounds == 7:
            await ctx.respond("Your character has taken too many wounds. Incapacitated.")
            return

        rolls = [random.randint(1, 10) for _ in range(amount + mod - health_status.penalty)]
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
            embed_color = VTMColors.GREEN
        elif result == 0:
            embed_title = "Unsuccessfully!"
            embed_color = VTMColors.WHITE
        else:
            embed_title = "Failure!"
            embed_color = VTMColors.RED
        embed_description = self.__get_roll_result_string(rolls)

        embed = Embed(title=embed_title, description=embed_description, color=embed_color)
        embed.add_field(name="Amount", value=str(amount))
        embed.add_field(name="Difficulty", value=str(difficulty))
        embed.add_field(name="Modifiers", value=str(mod))
        embed.add_field(name="Wounds", value=str(health_status))
        embed.add_field(name="Is special?", value=f"Yes (added {added_rolls})" if special else "No")
        embed.add_field(name="Result", value=f"{result} Successes")

        log.debug(
            "VTM: '%s' | A: %s | %s | D: %s | M: %s | W: %s | S: %s | R: %s",
            ctx.author.name,
            amount,
            rolls,
            difficulty,
            mod,
            health_status.penalty,
            special,
            result,
        )

        await ctx.respond(embed=embed)

    @vtm.command(name="soak", description="Calculates the amount of absorbed damage.")
    @option("damage", description="How much damage should the character be dealt?", min_value=1)
    @option("stamina", description="How much stamina does the character have?", min_value=0, max_value=10)
    @option("armor", description="What is the character's armor rating?", default=0, min_value=0)
    @option("mod", description="What will be the modifier?", default=0)
    @option("guaranteed", description="Guaranteed amount of damage absorbed.", default=0)
    async def vtm_soak(self, ctx: AppCtx, damage: int, stamina: int, armor: int, mod: int, guaranteed: int) -> None:
        rolls = [random.randint(1, 10) for _ in range(stamina + armor + mod)]

        difficult = 6
        absorbed_damage = 0
        for roll in rolls:
            if roll >= difficult:
                absorbed_damage += 1

        final_damage = max(damage - absorbed_damage - guaranteed, 0)

        if final_damage > 0:
            embed_title = f"{final_damage} damage done!"
            embed_color = VTMColors.RED
        else:
            embed_title = "All damage absorbed!"
            embed_color = VTMColors.GREEN
        embed_description = self.__get_roll_result_string(rolls)

        embed = Embed(title=embed_title, description=embed_description, color=embed_color)
        embed.add_field(name="Stamina", value=str(stamina))
        embed.add_field(name="Armor", value=str(armor))
        embed.add_field(name="Modifiers", value=str(mod))
        embed.add_field(name="Damage", value=str(damage))
        embed.add_field(name="Absorbed", value=str(absorbed_damage))
        embed.add_field(name="Guaranteed", value=str(guaranteed))
        embed.add_field(name="Final damage", value=str(final_damage))
        await ctx.respond(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(VTM(bot))
