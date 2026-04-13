import datetime
from applications.extensions import db


class SensitiveWord(db.Model):
    __tablename__ = 'wl_sensitive_word'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    word = db.Column(db.String(100), nullable=False, unique=True)
    severity = db.Column(db.Integer, default=1, comment='1=warning, 2=crisis popup')
    create_at = db.Column(db.DateTime, default=datetime.datetime.now)
