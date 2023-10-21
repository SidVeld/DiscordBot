from tortoise import fields
from tortoise.models import Model


class GrudgeModel(Model):
    grudge_id = fields.IntField(pk=True, unique=True)
    user = fields.ForeignKeyField("models.UserModel")
    title = fields.CharField(max_length=100)
    content = fields.CharField(max_length=300)
    created_at = fields.DatetimeField(auto_now_add=True)
    revenged = fields.BooleanField(default=False)
    revenged_at = fields.DatetimeField(null=True)

    class Meta:
        table = "grudge"
