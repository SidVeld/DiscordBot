from discord import InputTextStyle, ui
from discord.interactions import Interaction

from bot.models import GrudgeModel, UserModel


class AddGrudgeModal(ui.Modal):
    def __init__(self) -> None:
        super().__init__(title="Add new grudge")
        self.add_item(ui.InputText(label="Title", max_length=100, required=True))
        self.add_item(ui.InputText(label="Content", style=InputTextStyle.long, max_length=300, required=True))

    async def callback(self, interaction: Interaction) -> None:
        assert interaction.user
        user, _ = await UserModel.get_or_create(
            user_id=interaction.user.id, defaults={"username": interaction.user.name}
        )
        title = self.children[0].value
        content = self.children[1].value
        await GrudgeModel.create(title=title, content=content, user=user)
        await interaction.response.send_message("Done! New grudge added.", ephemeral=True)


class EditGrudgeModal(ui.Modal):
    __editable_grudge: GrudgeModel

    def __init__(self, grudge: GrudgeModel) -> None:
        super().__init__(title="Edit grudge")
        self.__editable_grudge = grudge
        self.add_item(
            ui.InputText(
                label="Title",
                max_length=100,
                required=True,
                value=grudge.title
            )
        )
        self.add_item(
            ui.InputText(
                label="Content",
                style=InputTextStyle.long,
                max_length=300,
                required=True,
                value=grudge.content
            )
        )

    async def callback(self, interaction: Interaction) -> None:
        new_title = self.children[0].value
        new_content = self.children[1].value
        assert new_title
        assert new_content

        self.__editable_grudge.title = new_title
        self.__editable_grudge.content = new_content
        await self.__editable_grudge.save()
        await interaction.response.send_message("Done! Grudge edited.")
