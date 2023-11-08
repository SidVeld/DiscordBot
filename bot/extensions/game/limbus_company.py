import random
from logging import getLogger

from discord import ApplicationContext as AppCtx
from discord import Bot, Embed, SlashCommandGroup, option

from bot.classes.extension import Extension

COINS = ["●", "○"]

COLORS = {
    "Red": 0xa0392b,
    "Orange": 0xbb521f,
    "Yellow": 0xdc8401,
    "Green": 0x5e7d28,
    "Light blue": 0x2c5d68,
    "Blue": 0x15497b,
    "Purple": 0x744888
}

COLOR_CHOICES = [color_name for color_name in COLORS.keys()]


log = getLogger()


class LimbusCompany(Extension):
    limbus = SlashCommandGroup("limbus")

    @limbus.command(name="coinflip", description="Rolls coin like in Limbus Company!")
    @option("amount", description="The number of coins to be tossed", min_value=1, max_value=10)
    @option("power", description="The starting power of the throw. The power of the coin is added to it.")
    @option("coin_power", description="The power of a coin. Will be added to the starting power.")
    @option("color", description="Color for result embed.", choices=COLOR_CHOICES)
    @option("hidden", description="Should the result of the command be hidden from the rest?")
    async def limbus_roll(
        self,
        ctx: AppCtx,
        amount: int = 1,
        power: int = 0,
        coin_power: int = 1,
        color: str = "None",
        hidden: bool = False
    ) -> None:
        coins = []
        additive_power = 0

        for _ in range(amount):
            if (coin := random.choice(COINS)) == COINS[0]:
                additive_power += coin_power
            coins.append(coin)

        result = power + additive_power

        embed = Embed(
            title="Coinflip result",
            description=" - ".join(coins) + f" | ***{result}***",
            color=COLORS[color] if color != "None" else Embed.Empty
        )
        embed.add_field(name="Coins", value=str(amount))
        embed.add_field(name="Power", value=str(power))
        embed.add_field(name="Coin power", value=str(coin_power))
        embed.add_field(name="Result", value=f"{power} + {additive_power} = {result}")

        await ctx.respond(embed=embed, ephemeral=hidden)


def setup(bot: Bot) -> None:
    bot.add_cog(LimbusCompany(bot))
