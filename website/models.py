from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import datetime


db = SQLAlchemy()
db_name = 'database.db'

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    text = db.Column(db.String(1000))
    date = db.Column(db.DateTime(timezone = True), default=datetime.datetime.now().replace(microsecond=0))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='note')
    likes = db.relationship('Like', backref='note', passive_deletes = True)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    date_created = db.Column(db.DateTime(timezone = True), default=datetime.datetime.now().replace(microsecond=0))
    date_modified = db.Column(db.DateTime(timezone = True), default=datetime.datetime.now().replace(microsecond=0))
    last_active = db.Column(db.DateTime(timezone = True), default=datetime.datetime.now().replace(microsecond=0))
    notes = db.relationship('Note', backref='user')
    comments = db.relationship('Comment', backref='user')
    likes = db.relationship('Like', backref='user', passive_deletes = True)
    picture = db.Column(db.String(300), default='default_picture.jpg')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100))
    date = db.Column(db.DateTime(timezone = True), default=datetime.datetime.now().replace(microsecond=0))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'))

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'))