import datetime
from applications.extensions import db


class Comment(db.Model):
    __tablename__ = 'wl_comment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('wl_post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('wl_comment.id'), nullable=True)
    create_at = db.Column(db.DateTime, default=datetime.datetime.now)
    delete_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref='comments')
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side='Comment.id'))
