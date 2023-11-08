from typing import TYPE_CHECKING

from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:
    from .user import UserModel


class GrudgeModel(Model):
    grudge_id = fields.IntField(pk=True, unique=True)
    user: fields.ForeignKeyRelation["UserModel"] = fields.ForeignKeyField("models.UserModel", related_name="grudges")
    title = fields.CharField(max_length=100)
    content = fields.CharField(max_length=300)
    created_at = fields.DatetimeField(auto_now_add=True)
    revenged = fields.BooleanField(default=False)
    revenged_at = fields.DatetimeField(null=True)

    class Meta:
        table = "grudge"
        table_description = "This table contains the user records of the grudges extension."
