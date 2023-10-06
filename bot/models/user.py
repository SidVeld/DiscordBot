from tortoise import fields
from tortoise.models import Model


class UserModel(Model):
    user_id = fields.IntField(pk=True, unique=True)
    discord_id = fields.BigIntField(unique=True)
    username = fields.TextField()
    registered_at = fields.DatetimeField(null=True, auto_now_add=True)

    class Meta:
        table = "user"
