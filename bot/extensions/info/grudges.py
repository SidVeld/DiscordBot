from logging import getLogger
from datetime import datetime
from typing import Literal

from discord import (
    ApplicationContext as AppCtx,
    Embed,
    Bot,
    SlashCommandGroup,
    ui,
    InputTextStyle,
    ButtonStyle,
    option
)
from discord.interactions import Interaction
from discord.ext.pages import Paginator, Page, PaginatorButton

from bot.classes.extension import Extension
from bot.models import UserModel, GrudgeModel


log = getLogger()


GRUDGE_MODAL_ACTIONS = Literal["add", "edit"]


class GrudgesModal(ui.Modal):
    __mode: GRUDGE_MODAL_ACTIONS

    def __init__(self, mode: GRUDGE_MODAL_ACTIONS) -> None:
        self.__mode = mode

        match self.__mode:
            case "add":
                super().__init__(title="Add new grudge")
            case "edit":
                super().__init__(title="Edit grudge")

        self.add_item(
            ui.InputText(
                label="Title",
                max_length=100,
                required=True
            )
        )

        self.add_item(
            ui.InputText(
                label="Content",
                style=InputTextStyle.long,
                max_length=300,
                required=True
            )
        )

    def fill_fields(self, grudge_title: str, grudge_content: str) -> None:
        self.children[0].value = grudge_title
        self.children[1].value = grudge_content

    async def __callback_add(self, interaction: Interaction) -> None:
        user = await UserModel.get(user_id=interaction.user.id)
        title = self.children[0].value
        content = self.children[1].value
        await GrudgeModel.create(title=title, content=content, user=user)

    async def __callback_edit(self) -> None:
        self.new_title = self.children[0].value
        self.new_content = self.children[1].value

    async def callback(self, interaction: Interaction) -> None:
        match self.__mode:
            case "add":
                await self.__callback_add(interaction)
            case "edit":
                await self.__callback_edit()

        await interaction.response.send_message("Done!", ephemeral=True)


class Grudges(Extension):
    grudges = SlashCommandGroup("grudges", "The Great Book of Grudges")

    @grudges.command(name="add", description="Adds new grudge.")
    async def add_grudge(self, ctx: AppCtx) -> None:
        await ctx.send_modal(GrudgesModal("add"))

    @grudges.command(name="delete", description="Deletes grudge.")
    @option(name="grudge_id", description="Grudge's id.")
    async def delete_grudge(self, ctx: AppCtx, grudge_id: int) -> None:
        grudge = await GrudgeModel.get_or_none(grudge_id=grudge_id)

        if grudge is None:
            await ctx.respond("Grudge with provided id is not exists.", ephemeral=True)
            return

        user = await grudge.user
        if user.user_id != ctx.author.id:
            await ctx.respond("You can't delete this grudge.", ephemeral=True)
            return

        await grudge.delete()

        await ctx.respond("Done!", ephemeral=True)

    @grudges.command(name="edit", description="Edits grudge.")
    @option(name="grudge_id", description="Grudge's id.")
    async def edit_grudge(self, ctx: AppCtx, grudge_id: int) -> None:
        grudge = await GrudgeModel.get_or_none(grudge_id=grudge_id)

        if grudge is None:
            await ctx.respond("Grudge with provided id is not exists.", ephemeral=True)
            return

        user = await grudge.user
        if user.user_id != ctx.author.id:
            await ctx.respond("You can't edit this grudge.", ephemeral=True)
            return

        modal = GrudgesModal("edit")
        modal.fill_fields(grudge.title, grudge.content)

        await ctx.send_modal(modal)
        await modal.wait()

        grudge.title = modal.new_title
        grudge.content = modal.new_content
        await grudge.save()

    def __get_raw_pages(self, grudges: list[GrudgeModel]):
        grudge_per_page: int = 3
        for index in range(0, len(grudges), grudge_per_page):
            yield grudges[index:index + grudge_per_page]

    def __get_page(self, raw_page: list[GrudgeModel]) -> Page:
        embeds = []
        for grudge in raw_page:
            embed = Embed(title=grudge.title, description=grudge.content, timestamp=grudge.created_at)

            if grudge.revenged:
                embed.title = f"[REVENGED] {embed.title}"
                embed.add_field(name="Revenged at", value=f"<t:{int(grudge.created_at.timestamp())}:f>")

            embed.set_footer(text=f"ID: {grudge.grudge_id}")

            embeds.append(embed)
        return Page(embeds=embeds)

    def __get_pages(self, grudges: list[GrudgeModel]) -> list[Page]:
        pages = []
        raw_pages = self.__get_raw_pages(grudges)
        for raw_page in raw_pages:
            pages.append(self.__get_page(raw_page))
        return pages

    @grudges.command(name="list", description="Lists your grudges")
    @option("compact", description="Should you view grudges in compact mode?")
    async def list_grudges(self, ctx: AppCtx, compact: bool = True) -> None:
        user = await UserModel.get(user_id=ctx.author.id)
        grudges = await user.grudges.all()
        grudges_len = len(grudges)
        log.debug(f"{user.username} ({user.user_id}) has {grudges_len}")

        if grudges_len < 1:
            await ctx.respond("No grudges!")
            return

        match compact:
            case False:
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

            case True:
                embed = Embed(title="Grudges: compact")
                grudges_strings = []
                for grudge in grudges:
                    title = f"[R] {grudge.title}" if grudge.revenged else grudge.title
                    grudges_strings.append(f"`{grudge.grudge_id}`: {title}")
                embed.description = "\n".join(grudges_strings)
                embed.set_footer(text=f"Total: {len(grudges)}")

                await ctx.respond(embed=embed)

    @grudges.command(name="mark_as", description="Marks grudge as revenged or unrevenged.")
    @option(name="grudge_id", description="Grudge's id.")
    @option(name="mark", description="New grudge's mark", choices=["revenged", "unrevenged"])
    async def mark_grudge_as(self, ctx: AppCtx, grudge_id: int, mark: str) -> None:
        grudge = await GrudgeModel.get_or_none(grudge_id=grudge_id)

        if grudge is None:
            await ctx.respond("Not exists", ephemeral=True)
            return

        user: UserModel = await grudge.user
        if user.user_id != ctx.author.id:
            await ctx.respond("You can't mark this grudge as revenged.", ephemeral=True)
            return

        match mark:
            case "revenged":
                if grudge.revenged:
                    await ctx.respond("Already marked as revenged.", ephemeral=True)
                    return

                grudge.revenged = True
                grudge.revenged_at = datetime.now()
                await grudge.save()

            case "unrevenged":
                if not grudge.revenged:
                    await ctx.respond("Already marked as unrevenged.", ephemeral=True)
                    return

                grudge.revenged = False
                grudge.revenged_at = None
                await grudge.save()

        await ctx.respond("Done!", ephemeral=True)


def setup(bot: Bot) -> None:
    bot.add_cog(Grudges(bot))
