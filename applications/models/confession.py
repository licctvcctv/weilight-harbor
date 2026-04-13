import datetime
from applications.extensions import db


class Confession(db.Model):
    __tablename__ = 'wl_confession'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    nickname = db.Column(db.String(50))
    session_id = db.Column(db.String(100))
    hug_count = db.Column(db.Integer, default=0)
    create_at = db.Column(db.DateTime, default=datetime.datetime.now)
