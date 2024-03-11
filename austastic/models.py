import inspect
import sys
from datetime import datetime

from peewee import CharField, Check, DateTimeField, ForeignKeyField, IntegerField, Model, Field
from loguru import logger

from austastic.database import database


def hex_from_id(id: int) -> str:
    return format(id, 'x')


def id_from_hex(hex: str) -> int:
    return int(hex, 16)


class HexField(IntegerField):
    def db_value(self, value):
        return int(value, 16)

    def python_value(self, value):
        return format(value, 'x')


class SQLiteModel(Model):
    class Meta:
        database = database


class User(SQLiteModel):
    discord_id = IntegerField(primary_key=True)


class Node(SQLiteModel):
    id = IntegerField(primary_key=True, unique=True, constraints=[Check('id <= 4294967295')])
    long_name = CharField(null=True)
    owner = ForeignKeyField(User, null=True)
    hardware = CharField(null=True)
    hex = HexField(unique=True)

    @property
    def hex_suffix(self) -> str:
        return self.hex[-4:]

    # peewee doesn't have a validator native decorator
    # @validator('id')
    # def validate_id(cls, value):
    #     if isinstance(value, str):
    #         if re.match(r'^[0-9A-Fa-f]+$', value):
    #             return int(value, 16)
    #         else:
    #             raise ValueError("ID must be either an integer or a hexadecimal value")
    #     return value


class Sighting(SQLiteModel):
    node = ForeignKeyField(Node, backref="sightings")
    user = ForeignKeyField(User)
    timestamp = DateTimeField(default=datetime.now)


def create_tables() -> list[Model]:
    models = [
        cls
        for _, cls in inspect.getmembers(
            sys.modules[__name__], lambda obj: inspect.isclass(obj) and issubclass(obj, SQLiteModel) and obj != SQLiteModel
        )
    ]

    database.create_tables(models)
    logger.info(f"Tables created: {models}")
    return models
