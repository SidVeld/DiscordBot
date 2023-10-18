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


class GrudgeModal(ui.Modal):
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

    async def __callback_edit(self, interaction: Interaction) -> None:
        self.new_title = self.children[0].value
        self.new_content = self.children[1].value

    async def callback(self, interaction: Interaction) -> None:
        match self.__mode:
            case "add":
                await self.__callback_add(interaction)
            case "edit":
                await self.__callback_edit(interaction)

        await interaction.response.send_message("Done!", ephemeral=True)


class Grudge(Extension):
    grudges = SlashCommandGroup("grudges", "The Great Book of Grudges")

    @grudges.command(name="add", description="Adds new grudge.")
    async def add_grudge(self, ctx: AppCtx) -> None:
        await ctx.send_modal(GrudgeModal("add"))

    @grudges.command(name="delete", description="Deletes grudge.")
    @option(name="grudge_id", description="Grudge's id.")
    async def delete_grudge(self, ctx: AppCtx, grudge_id: int) -> None:
        grudge = await GrudgeModel.get_or_none(grudge_id=grudge_id)

        if grudge is None:
            await ctx.respond("Grudge with provided id is not exists.", ephemeral=True)
            return

        user: UserModel = await grudge.user
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

        user: UserModel = await grudge.user
        if user.user_id != ctx.author.id:
            await ctx.respond("You can't edit this grudge.", ephemeral=True)
            return

        modal = GrudgeModal("edit")
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
                embed.add_field(name="Expunged at", value=f"<t:{int(grudge.created_at.timestamp())}:f>")

            embed.set_footer(text=f"ID: {grudge.grudge_id}")

            embeds.append(embed)
        return Page(embeds=embeds)

    def __get_pages(self, grudges: list[GrudgeModel]) -> list[Page]:
        pages = []
        raw_pages = self.__get_raw_pages(grudges)
        log.debug(f"The raw pages is {raw_pages}")
        for raw_page in raw_pages:
            pages.append(self.__get_page(raw_page))
        return pages

    @grudges.command(name="list", description="Lists your grudges")
    async def list_grudges(self, ctx: AppCtx) -> None:
        grudges = await GrudgeModel.filter(user_id=ctx.author.id)

        if len(grudges) < 1:
            await ctx.respond("No grudges!")
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

    @grudges.command(name="compact", description="Sends embed with sorted grudges.")
    async def get_compact_grudges(self, ctx: AppCtx) -> None:
        grudges = await GrudgeModel.filter(user_id=ctx.author.id).order_by("grudge_id")

        embed = Embed(title="Grudges")

        if len(grudges) < 1:
            embed.description = "No grudges found!"
            await ctx.respond(embed=embed)
            return

        grudges_strings = []
        for grudge in grudges:
            if grudge.revenged:
                grudges_strings.append(f"{grudge.grudge_id}: [R] {grudge.title}")
                continue
            grudges_strings.append(f"{grudge.grudge_id}: {grudge.title}")
        embed.description = "\n".join(grudges_strings)

        await ctx.respond(embed=embed)

    @grudges.command(name="mark_as_revenged", description="Marks grudge as revenged.")
    @option(name="grudge_id", description="Grudge's id.")
    async def mark_grudge_as_revenged(self, ctx: AppCtx, grudge_id: int) -> None:
        grudge = await GrudgeModel.get_or_none(grudge_id=grudge_id)

        if grudge is None:
            await ctx.respond("Not exists", ephemeral=True)
            return

        user: UserModel = await grudge.user
        if user.user_id != ctx.author.id:
            await ctx.respond("You can't mark this grudge as revenged.", ephemeral=True)
            return

        if grudge.revenged:
            await ctx.respond("Already marked as revenged.", ephemeral=True)
            return

        grudge.revenged = True
        grudge.revenged_at = datetime.now()
        await grudge.save()

        await ctx.respond("Done!", ephemeral=True)


def setup(bot: Bot) -> None:
    bot.add_cog(Grudge(bot))
