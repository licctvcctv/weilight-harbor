from sqlalchemy import func
from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from applications.extensions import db
from applications.models.campaign import Campaign
from applications.models.donation import Donation
from applications.common.utils.files import save_upload
from applications.view.crowdfunding import crowdfunding_bp

CAMPAIGN_CATEGORIES = [
    ('cancer', 'Cancer'),
    ('rare_disease', 'Rare Disease'),
    ('pediatric', 'Pediatric'),
    ('chronic', 'Chronic Illness'),
    ('mental_health', 'Mental Health'),
    ('other', 'Other'),
]


@crowdfunding_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'newest')
    category = request.args.get('category', 'all')

    query = Campaign.query.options(joinedload(Campaign.user)).filter_by(status='approved')
    if category != 'all':
        query = query.filter_by(category=category)

    if sort == 'progress':
        query = query.order_by(Campaign.current_amount.desc())
    elif sort == 'urgent':
        query = query.order_by(Campaign.current_amount.asc())
    else:
        query = query.order_by(Campaign.create_at.desc())

    pagination = query.paginate(page=page, per_page=12, error_out=False)
    campaigns = list(pagination.items)
    donor_counts = {}
    if campaigns:
        counts = db.session.query(
            Donation.campaign_id,
            func.count(Donation.id)
        ).filter(
            Donation.campaign_id.in_([campaign.id for campaign in campaigns])
        ).group_by(Donation.campaign_id).all()
        donor_counts = {campaign_id: count for campaign_id, count in counts}

    for campaign in campaigns:
        campaign.donor_count = donor_counts.get(campaign.id, 0)

    categories_with_all = [('all', 'All')] + CAMPAIGN_CATEGORIES

    return render_template('public/crowdfunding/index.html',
                           campaigns=campaigns, pagination=pagination,
                           categories=categories_with_all, current_category=category,
                           current_sort=sort)


@crowdfunding_bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    if not q:
        return redirect(url_for('crowdfunding.index'))
    campaigns = Campaign.query.options(joinedload(Campaign.user)).filter(
        Campaign.status == 'approved',
        db.or_(Campaign.title.ilike(f'%{q}%'), Campaign.description.ilike(f'%{q}%'))
    ).order_by(Campaign.create_at.desc()).limit(20).all()
    return render_template('public/crowdfunding/index.html',
                           campaigns=campaigns, pagination=None,
                           categories=[('all', 'All')] + CAMPAIGN_CATEGORIES,
                           current_category='all', current_sort='newest',
                           search_query=q)


@crowdfunding_bp.route('/my')
@login_required
def my_campaigns():
    return redirect(url_for('user_center.history', tab='campaigns'))


@crowdfunding_bp.route('/campaign/<int:campaign_id>')
def detail(campaign_id):
    campaign = Campaign.query.options(joinedload(Campaign.user)).get_or_404(campaign_id)
    if campaign.status != 'approved' and (not current_user.is_authenticated or current_user.id != campaign.user_id):
        flash('This campaign is not available.', 'error')
        return redirect(url_for('crowdfunding.index'))

    donations = Donation.query.options(joinedload(Donation.user)).filter_by(
        campaign_id=campaign_id
    ).order_by(Donation.create_at.desc()).limit(100).all()
    donor_count = Donation.query.filter_by(campaign_id=campaign_id).count()

    progress = 0
    goal = float(campaign.funding_goal) if campaign.funding_goal else 0
    if goal > 0:
        progress = min(100, round(float(campaign.current_amount) / goal * 100, 1))

    return render_template('public/crowdfunding/detail.html',
                           campaign=campaign, donations=donations,
                           donor_count=donor_count, progress=progress)


@crowdfunding_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_campaign():
    if not current_user.is_certified:
        flash('Only certified caregivers can create campaigns. Please apply for certification first.', 'error')
        return redirect(url_for('user_center.certification'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()[:200]
        description = request.form.get('description', '').strip()[:5000]
        category = request.form.get('category', 'other')
        funding_goal = request.form.get('funding_goal', 0, type=float)
        if category not in dict(CAMPAIGN_CATEGORIES):
            category = 'other'

        if not title or not description or funding_goal < 100:
            flash('Please fill in all required fields. Minimum goal is 100 yuan.', 'error')
            return render_template('public/crowdfunding/create.html',
                                   categories=CAMPAIGN_CATEGORIES)

        qr_code_url = save_upload(
            request.files.get('qr_code'), 'campaigns', 'qr'
        )
        if not qr_code_url:
            flash('A valid payment QR code is required for campaign review.', 'error')
            return render_template('public/crowdfunding/create.html',
                                   categories=CAMPAIGN_CATEGORIES)

        campaign = Campaign(
            user_id=current_user.id, title=title, description=description,
            category=category, funding_goal=funding_goal, status='pending',
            qr_code_url=qr_code_url
        )

        if 'cover_image' in request.files:
            campaign.cover_image = save_upload(
                request.files['cover_image'], 'campaigns', 'cover')
        if 'patient_photo' in request.files:
            campaign.patient_photo = save_upload(
                request.files['patient_photo'], 'campaigns', 'patient')
        db.session.add(campaign)
        db.session.commit()
        flash('Campaign submitted for review! We will review it within 24 hours.', 'success')
        return redirect(url_for('crowdfunding.detail', campaign_id=campaign.id))

    return render_template('public/crowdfunding/create.html',
                           categories=CAMPAIGN_CATEGORIES)


@crowdfunding_bp.route('/campaign/<int:campaign_id>/donate', methods=['POST'])
@login_required
def donate(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.status != 'approved' or campaign.is_fully_funded:
        return jsonify({'error': 'This campaign is not accepting donations.'}), 400
    if not campaign.qr_code_url:
        return jsonify({'error': 'Payment QR code is not available for this campaign.'}), 400

    data = request.get_json(silent=True) or {}
    payment_method = data.get('payment_method', 'wechat')
    if payment_method not in ['wechat', 'alipay']:
        return jsonify({'error': 'Invalid payment method.'}), 400
    if data.get('payment_confirmed') is not True:
        return jsonify({'error': 'Please complete the payment confirmation before recording the donation.'}), 402

    try:
        amount = float(data.get('amount', 0))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid amount.'}), 400

    if amount < 1:
        return jsonify({'error': 'Minimum donation is 1 yuan.'}), 400

    db.session.add(Donation(
        campaign_id=campaign_id, user_id=current_user.id,
        amount=amount,
        message=data.get('message', '').strip()[:200],
        is_anonymous=bool(data.get('is_anonymous', False))
    ))

    campaign.current_amount = float(campaign.current_amount) + amount
    goal = float(campaign.funding_goal)
    if float(campaign.current_amount) >= goal:
        campaign.is_fully_funded = True

    db.session.commit()

    progress = min(100, round(float(campaign.current_amount) / goal * 100, 1))
    donor_count = Donation.query.filter_by(campaign_id=campaign_id).count()

    return jsonify({
        'success': True,
        'current_amount': float(campaign.current_amount),
        'funding_goal': goal,
        'progress': progress,
        'is_fully_funded': campaign.is_fully_funded,
        'donor_count': donor_count
    })
