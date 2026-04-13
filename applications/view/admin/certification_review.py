import datetime
from flask import Blueprint, render_template, request
from flask_login import current_user
from sqlalchemy.orm import joinedload
from applications.extensions import db
from applications.models.certification import Certification
from applications.models import User, Role
from applications.common.utils.http import success_api, fail_api, table_api
from applications.common.utils.rights import authorize

admin_cert = Blueprint('adminCert', __name__, url_prefix='/admin/certification')


@admin_cert.get('/')
@authorize("admin:certification:main", log=True)
def main():
    return render_template('admin/certification/main.html')


@admin_cert.get('/data')
@authorize("admin:certification:main", log=True)
def data():
    status_filter = request.args.get('status', '')
    query = Certification.query.options(joinedload(Certification.user))
    if status_filter:
        query = query.filter_by(status=status_filter)
    query = query.order_by(Certification.create_at.desc())

    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    pagination = query.paginate(page=page, per_page=limit, error_out=False)

    result = []
    for c in pagination.items:
        result.append({
            'id': c.id,
            'username': c.user.username if c.user else '',
            'cert_type': c.cert_type,
            'real_name': c.real_name,
            'relation': c.relation or '',
            'document_url': c.document_url or '',
            'status': c.status,
            'reject_reason': c.reject_reason or '',
            'create_at': c.create_at.strftime('%Y-%m-%d %H:%M') if c.create_at else ''
        })
    return table_api(data=result, count=pagination.total)


@admin_cert.put('/approve/<int:cert_id>')
@authorize("admin:certification:edit", log=True)
def approve(cert_id):
    cert = Certification.query.get(cert_id)
    if not cert:
        return fail_api(msg="Not found")
    cert.status = 'approved'
    cert.reviewer_id = current_user.id
    cert.reviewed_at = datetime.datetime.now()

    # Update user type and certification status
    user = User.query.get(cert.user_id)
    if user:
        if cert.cert_type == 'family':
            user.user_type = 'certified_family'
        else:
            user.user_type = 'certified_volunteer'
        user.is_certified = True
        # Add certified role
        role_code = 'certified_family' if cert.cert_type == 'family' else 'certified_volunteer'
        role = Role.query.filter_by(code=role_code).first()
        if role and role not in user.role.all():
            user.role.append(role)

    db.session.commit()
    return success_api(msg="Approved")


@admin_cert.put('/reject/<int:cert_id>')
@authorize("admin:certification:edit", log=True)
def reject(cert_id):
    cert = Certification.query.get(cert_id)
    if not cert:
        return fail_api(msg="Not found")
    cert.status = 'rejected'
    cert.reject_reason = request.json.get('reason', 'Application rejected')
    cert.reviewer_id = current_user.id
    cert.reviewed_at = datetime.datetime.now()
    db.session.commit()
    return success_api(msg="Rejected")
