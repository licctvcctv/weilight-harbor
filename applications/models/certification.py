import datetime
from applications.extensions import db


class Certification(db.Model):
    __tablename__ = 'wl_certification'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=False)
    cert_type = db.Column(db.String(20), comment='family or volunteer')
    real_name = db.Column(db.String(50))
    id_card = db.Column(db.String(30))
    relation = db.Column(db.String(50))
    document_url = db.Column(db.String(255))
    patient_name = db.Column(db.String(50), comment='Patient name')
    patient_illness = db.Column(db.String(100), comment='Patient illness type')
    hospital_name = db.Column(db.String(100), comment='Hospital name')
    diagnosis_date = db.Column(db.Date, nullable=True, comment='Diagnosis date')
    additional_docs = db.Column(db.Text, comment='JSON array of additional document URLs')
    status = db.Column(db.String(20), default='pending')
    reject_reason = db.Column(db.String(500))
    reviewer_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    create_at = db.Column(db.DateTime, default=datetime.datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    user = db.relationship('User', foreign_keys=[user_id], backref='certifications')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id])
