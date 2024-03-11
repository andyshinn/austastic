import os

from peewee import SqliteDatabase

db_name = os.getenv("DB_NAME", "meshtastic.db")
database = SqliteDatabase(db_name)
database.connect()