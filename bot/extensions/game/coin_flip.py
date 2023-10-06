import random

from logging import getLogger

from discord import ApplicationContext as AppCtx, slash_command, Embed, Bot, option

from bot.classes.extension import Extension


log = getLogger()


COINS = ["●", "○"]


class CoinFlip(Extension):
    @slash_command(name="coin_flip", description="Flip the coin!")
    @option("amount", description="The number of coins to be tossed", min_value=1, max_value=10)
    @option("coin_power", description="The power of a coin. Will be added to the starting power.")
    @option("start_power", description="The starting power of the throw. The power of the coin is added to it.")
    @option("hidden", description="Should the result of the command be hidden from the rest?")
    async def coin_flip_command(
        self, ctx: AppCtx, amount: int = 1, coin_power: int = 1, start_power: int = 0, hidden: bool = False
    ) -> None:
        result = []
        total_power = 0

        for _ in range(amount):
            if (choice := random.choice(COINS)) == COINS[0]:
                total_power += coin_power
            result.append(choice)

        result_embed = Embed(
            title=f"Result: {start_power + total_power}",
            description=" ".join(result) + f" ***{total_power}***"
        )

        await ctx.respond(embed=result_embed, ephemeral=hidden)


def setup(bot: Bot) -> None:
    bot.add_cog(CoinFlip(bot))
