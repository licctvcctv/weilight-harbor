import json
import datetime
from applications.extensions import db


class JournalEntry(db.Model):
    __tablename__ = 'wl_journal_entry'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=False)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    images = db.Column(db.Text, comment='JSON array of image URLs')
    mood = db.Column(db.String(20))
    entry_date = db.Column(db.Date, default=datetime.date.today)
    create_at = db.Column(db.DateTime, default=datetime.datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    delete_at = db.Column(db.DateTime, nullable=True)

    @property
    def parsed_images(self):
        if not self.images:
            return []
        try:
            return json.loads(self.images)
        except (TypeError, ValueError):
            return []

    user = db.relationship('User', backref='journal_entries')
