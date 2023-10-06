from discord import Bot, Cog


class Extension(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
