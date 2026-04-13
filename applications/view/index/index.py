from flask import render_template, request, session, jsonify, Blueprint
from flask_login import current_user
from applications.extensions import db

index_bp = Blueprint('Index', __name__, url_prefix='/')


@index_bp.route('/')
def index():
    from applications.models.campaign import Campaign
    from applications.models.post import Post
    from applications.models.donation import Donation
    from applications.models import User
    from sqlalchemy import func

    # Real stats
    user_count = User.query.count()
    campaign_count = Campaign.query.filter_by(status='approved').count()
    total_raised = db.session.query(func.coalesce(func.sum(Donation.amount), 0)).scalar()

    # Featured campaigns (latest 3 approved)
    featured_campaigns = Campaign.query.filter_by(status='approved').order_by(Campaign.create_at.desc()).limit(3).all()

    # Recent community posts (latest 4)
    recent_posts = Post.query.filter(Post.status == 1, Post.delete_at.is_(None)).order_by(Post.create_at.desc()).limit(4).all()

    return render_template('public/index.html',
                           user_count=user_count, campaign_count=campaign_count,
                           total_raised=float(total_raised),
                           featured_campaigns=featured_campaigns,
                           recent_posts=recent_posts)


@index_bp.route('/about')
def about():
    return render_template('public/about.html')


@index_bp.route('/help')
def help_page():
    return render_template('public/help.html')


@index_bp.route('/privacy')
def privacy():
    return render_template('public/privacy.html')


@index_bp.route('/terms')
def terms():
    return render_template('public/terms.html')


@index_bp.route('/set-locale', methods=['POST'])
def set_locale():
    data = request.get_json(silent=True) or {}
    locale = data.get('locale', 'en')
    if locale in ('zh', 'en'):
        session['locale'] = locale
        if current_user.is_authenticated:
            current_user.locale = locale
            db.session.commit()
    return jsonify(success=True)
