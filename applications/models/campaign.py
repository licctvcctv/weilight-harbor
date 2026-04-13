import datetime
from applications.extensions import db


class Campaign(db.Model):
    __tablename__ = 'wl_campaign'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    patient_photo = db.Column(db.String(255))
    cover_image = db.Column(db.String(255))
    funding_goal = db.Column(db.Numeric(10, 2), nullable=False)
    current_amount = db.Column(db.Numeric(10, 2), default=0.00)
    qr_code_url = db.Column(db.String(255))
    status = db.Column(db.String(20), default='draft')
    reject_reason = db.Column(db.String(500))
    reviewer_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    is_fully_funded = db.Column(db.Boolean, default=False)
    create_at = db.Column(db.DateTime, default=datetime.datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    delete_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', foreign_keys=[user_id], backref='campaigns')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id])
    donations = db.relationship('Donation', backref='campaign', cascade='all, delete-orphan')
