import datetime
from applications.extensions import db


class Donation(db.Model):
    __tablename__ = 'wl_donation'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('wl_campaign.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    message = db.Column(db.String(200))
    is_anonymous = db.Column(db.Boolean, default=False)
    create_at = db.Column(db.DateTime, default=datetime.datetime.now)

    user = db.relationship('User', backref='donations')
