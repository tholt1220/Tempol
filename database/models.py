# models.py
from .db import db

class Song(db.Document):
    title = db.StringField(required=True)
    tempo = db.IntField(required=True)
    filename = db.StringField(required=True)