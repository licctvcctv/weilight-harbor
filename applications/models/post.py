import json
import datetime
from applications.extensions import db


class Post(db.Model):
    __tablename__ = 'wl_post'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='all')
    images = db.Column(db.Text, comment='JSON array of image URLs')
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    is_anonymous = db.Column(db.Boolean, default=False)
    status = db.Column(db.Integer, default=1, comment='1=visible, 0=hidden')
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

    user = db.relationship('User', backref='posts')
    comments = db.relationship('Comment', backref='post', cascade='all, delete-orphan')
    likes = db.relationship('PostLike', backref='post', cascade='all, delete-orphan')
