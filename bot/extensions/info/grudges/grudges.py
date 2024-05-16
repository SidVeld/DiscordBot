from datetime import datetime

from discord import ApplicationContext as AppCtx
from discord import Bot, ButtonStyle, Embed, SlashCommandGroup, option
from discord.ext.pages import Page, Paginator, PaginatorButton

from bot.classes.extension import Extension
from bot.models import GrudgeModel, UserModel

from ._modals import AddGrudgeModal, EditGrudgeModal


class Grudges(Extension):
    grudge = SlashCommandGroup("grudge", "The Great Book of Grudges")

    @grudge.command(name="add", description="Adds new grudge.")
    async def add_grudge(self, ctx: AppCtx) -> None:
        await ctx.send_modal(AddGrudgeModal())

    @grudge.command(name="delete", description="Deletes grudge.")
    @option(name="grudge_id", description="Grudge's id.")
    async def delete_grudge(self, ctx: AppCtx, grudge_id: int) -> None:
        grudge = await GrudgeModel.get_or_none(grudge_id=grudge_id)

        if grudge is None:
            await ctx.respond("Grudge with provided id is not exists.", ephemeral=True)
            return

        if ctx.author.id != (await grudge.user).user_id:
            await ctx.respond("You can't delete this grudge.", ephemeral=True)
            return

        await grudge.delete()

        await ctx.respond("Done!", ephemeral=True)

    @grudge.command(name="edit", description="Edits grudge.")
    @option(name="grudge_id", description="Grudge's id.")
    async def edit_grudge(self, ctx: AppCtx, grudge_id: int) -> None:
        grudge = await GrudgeModel.get_or_none(grudge_id=grudge_id)

        if grudge is None:
            await ctx.respond("Grudge with provided id is not exists.", ephemeral=True)
            return

        if ctx.author.id != (await grudge.user).user_id:
            await ctx.respond("You can't edit this grudge.", ephemeral=True)
            return

        modal = EditGrudgeModal(grudge)
        await ctx.send_modal(modal)

    def __get_raw_pages(self, grudges: list[GrudgeModel]):
        grudge_per_page: int = 3
        for index in range(0, len(grudges), grudge_per_page):
            yield grudges[index:index + grudge_per_page]

    def __get_page(self, raw_page: list[GrudgeModel]) -> Page:
        embeds = []
        for grudge in raw_page:
            embed = Embed(title=grudge.title, description=grudge.content)
            embed.add_field(name="Created at", value=f"<t:{int(grudge.created_at.timestamp())}:f>")

            if grudge.revenged:
                embed.title = f"[REVENGED] {embed.title}"
                embed.add_field(name="Revenged at", value=f"<t:{int(grudge.revenged_at.timestamp())}:f>")

            embed.set_footer(text=f"ID: {grudge.grudge_id}")
            embeds.append(embed)

        return Page(embeds=embeds)

    def __get_pages(self, grudges: list[GrudgeModel]) -> list[Page]:
        pages = []
        raw_pages = self.__get_raw_pages(grudges)
        for raw_page in raw_pages:
            pages.append(self.__get_page(raw_page))
        return pages

    @grudge.command(name="list", description="Lists your grudges")
    @option("compact", description="Should you view grudges in compact mode?")
    @option("hidden", description="Should you view grudges in private view?")
    async def list_grudges(self, ctx: AppCtx, compact: bool = True, hidden: bool = True) -> None:
        user, _ = await UserModel.get_or_create(
            user_id=ctx.author.id,
            defaults={"username": ctx.author.name},
        )

        grudges = await user.grudges.all()

        if len(grudges) < 1:
            await ctx.respond("No grudges!")
            return

        if compact:
            embed = Embed(title="Grudges: compact")
            grudges_strings = []
            for grudge in grudges:
                title = f"[R] {grudge.title}" if grudge.revenged else grudge.title
                grudges_strings.append(f"`{grudge.grudge_id}`: {title}")
            embed.description = "\n".join(grudges_strings)
            embed.set_footer(text=f"Total: {len(grudges)}")

            await ctx.respond(embed=embed, ephemeral=hidden)
            return

        buttons = [
            PaginatorButton("first", "<<", style=ButtonStyle.gray),
            PaginatorButton("prev", "<", style=ButtonStyle.green),
            PaginatorButton("page_indicator", style=ButtonStyle.gray, disabled=True),
            PaginatorButton("next", ">", style=ButtonStyle.green),
            PaginatorButton("last", ">>", style=ButtonStyle.gray)
        ]
        paginator = Paginator(
            self.__get_pages(grudges),
            show_indicator=True,
            use_default_buttons=False,
            custom_buttons=buttons
        )
        await paginator.respond(ctx.interaction)

    @grudge.command(name="mark_as_revenged", description="Marks grudge as revenged or unrevenged.")
    @option(name="grudge_id", description="Grudge's id.")
    async def mark_grudge_as(self, ctx: AppCtx, grudge_id: int) -> None:
        grudge = await GrudgeModel.get_or_none(grudge_id=grudge_id)

        if grudge is None:
            await ctx.respond("Not exists", ephemeral=True)
            return

        if ctx.author.id != (await grudge.user).user_id:
            await ctx.respond("You can't mark this grudge as revenged.", ephemeral=True)
            return

        grudge.revenged = True
        grudge.revenged_at = datetime.now()
        await grudge.save()

        await ctx.respond("Done!", ephemeral=True)


def setup(bot: Bot) -> None:
    bot.add_cog(Grudges(bot))
