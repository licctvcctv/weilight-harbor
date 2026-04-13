import datetime
from applications.extensions import db


class PostLike(db.Model):
    __tablename__ = 'wl_post_like'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('wl_post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=False)
    create_at = db.Column(db.DateTime, default=datetime.datetime.now)

    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='uq_post_like'),)
    user = db.relationship('User', backref='post_likes')
