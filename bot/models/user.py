from tortoise import fields
from tortoise.models import Model

from .grudge import GrudgeModel


class UserModel(Model):
    user_id = fields.BigIntField(pk=True, unique=True)
    username = fields.TextField()
    added_at = fields.DatetimeField(auto_now_add=True)

    grudges: fields.ReverseRelation["GrudgeModel"]

    class Meta:
        table = "discord_user"
        table_description = "This table contains the users interacting with the bot."
