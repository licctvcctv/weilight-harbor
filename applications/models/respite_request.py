import datetime
from applications.extensions import db


class RespiteRequest(db.Model):
    __tablename__ = 'wl_respite_request'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=False)
    request_type = db.Column(db.String(20), comment='service or equipment')
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    province = db.Column(db.String(50))
    city = db.Column(db.String(50))
    district = db.Column(db.String(50))
    address = db.Column(db.String(255))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    pin_color = db.Column(db.String(10), default='blue')
    time_limit = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')
    acceptor_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=True)
    accepted_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    create_at = db.Column(db.DateTime, default=datetime.datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    delete_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', foreign_keys=[user_id], backref='respite_requests')
    acceptor = db.relationship('User', foreign_keys=[acceptor_id], backref='accepted_requests')
