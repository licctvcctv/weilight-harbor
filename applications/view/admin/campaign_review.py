import datetime
from flask import Blueprint, render_template, request
from flask_login import current_user
from sqlalchemy.orm import joinedload
from applications.extensions import db
from applications.models.campaign import Campaign
from applications.common.utils.http import success_api, fail_api, table_api
from applications.common.utils.rights import authorize

admin_campaign = Blueprint('adminCampaign', __name__, url_prefix='/admin/campaign-review')


@admin_campaign.get('/')
@authorize("admin:campaign:main", log=True)
def main():
    return render_template('admin/campaign_review/main.html')


@admin_campaign.get('/data')
@authorize("admin:campaign:main", log=True)
def data():
    status_filter = request.args.get('status', '')
    query = Campaign.query.options(joinedload(Campaign.user))
    if status_filter:
        query = query.filter_by(status=status_filter)
    query = query.order_by(Campaign.create_at.desc())

    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    pagination = query.paginate(page=page, per_page=limit, error_out=False)

    result = []
    for c in pagination.items:
        result.append({
            'id': c.id,
            'username': c.user.username if c.user else '',
            'title': c.title,
            'category': c.category or '',
            'funding_goal': float(c.funding_goal) if c.funding_goal else 0,
            'current_amount': float(c.current_amount) if c.current_amount else 0,
            'status': c.status,
            'cover_image': c.cover_image or '',
            'qr_code_url': c.qr_code_url or '',
            'reject_reason': c.reject_reason or '',
            'create_at': c.create_at.strftime('%Y-%m-%d %H:%M') if c.create_at else ''
        })
    return table_api(data=result, count=pagination.total)


@admin_campaign.put('/approve/<int:campaign_id>')
@authorize("admin:campaign:edit", log=True)
def approve(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return fail_api(msg="Not found")
    if not campaign.qr_code_url:
        return fail_api(msg="Payment QR code is required before approval")
    campaign.status = 'approved'
    campaign.reviewer_id = current_user.id
    campaign.reviewed_at = datetime.datetime.now()
    db.session.commit()
    return success_api(msg="Approved")


@admin_campaign.put('/reject/<int:campaign_id>')
@authorize("admin:campaign:edit", log=True)
def reject(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return fail_api(msg="Not found")
    campaign.status = 'rejected'
    data = request.get_json(silent=True) or {}
    campaign.reject_reason = data.get('reason', 'Campaign rejected')
    campaign.reviewer_id = current_user.id
    campaign.reviewed_at = datetime.datetime.now()
    db.session.commit()
    return success_api(msg="Rejected")
