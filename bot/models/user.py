from tortoise import fields
from tortoise.models import Model


class UserModel(Model):
    user_id = fields.BigIntField(pk=True, unique=True)
    username = fields.TextField()
    added_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "discord_user"
