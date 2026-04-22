import json
import datetime
import re
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from applications.extensions import db
from applications.models import User
from applications.models.certification import Certification
from applications.models.post import Post
from applications.models.campaign import Campaign
from applications.models.donation import Donation
from applications.models.respite_request import RespiteRequest
from applications.common.utils.files import save_upload, ALLOWED_DOC_EXTS
from applications.view.user_center import user_center_bp


@user_center_bp.route('/profile')
@login_required
def profile():
    posts_query = Post.query.filter_by(user_id=current_user.id).filter(Post.delete_at.is_(None))
    campaigns_query = Campaign.query.filter_by(user_id=current_user.id)
    donations_query = Donation.query.filter_by(user_id=current_user.id)

    posts = posts_query.order_by(Post.create_at.desc()).limit(5).all()
    campaigns = campaigns_query.order_by(Campaign.create_at.desc()).limit(5).all()
    donations = donations_query.order_by(Donation.create_at.desc()).limit(5).all()
    cert = Certification.query.filter_by(user_id=current_user.id).order_by(Certification.create_at.desc()).first()
    days_active = (datetime.datetime.now() - current_user.create_at).days if current_user.create_at else 0
    return render_template('public/user/profile.html',
                           posts=posts, campaigns=campaigns, donations=donations,
                           post_count=posts_query.count(),
                           campaign_count=campaigns_query.count(),
                           donation_count=donations_query.count(),
                           cert=cert, days_active=days_active)


@user_center_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        phone = re.sub(r'\D', '', request.form.get('phone', '').strip())[:20]
        email = request.form.get('email', '').strip()[:120]
        if phone and not re.fullmatch(r'\d{6,20}', phone):
            flash('Please enter a valid phone number.', 'error')
            return redirect(url_for('user_center.edit_profile'))
        if phone and User.query.filter(User.id != current_user.id, User.phone == phone).first():
            flash('Phone number is already in use.', 'error')
            return redirect(url_for('user_center.edit_profile'))
        if email and User.query.filter(User.id != current_user.id, User.email == email).first():
            flash('Email is already in use.', 'error')
            return redirect(url_for('user_center.edit_profile'))

        current_user.realname = request.form.get('realname', '').strip()[:20]
        current_user.phone = phone
        current_user.email = email
        current_user.bio = request.form.get('bio', '').strip()[:500]

        if 'avatar' in request.files:
            url = save_upload(request.files['avatar'], 'avatars', 'avatar')
            if url:
                current_user.avatar = url

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user_center.profile'))
    return render_template('public/user/edit_profile.html')


@user_center_bp.route('/certification', methods=['GET', 'POST'])
@login_required
def certification():
    existing = Certification.query.filter_by(user_id=current_user.id).order_by(Certification.create_at.desc()).first()
    if request.method == 'POST':
        if existing and existing.status == 'pending':
            flash('You already have a pending application.', 'error')
            return redirect(url_for('user_center.certification'))

        cert_type = request.form.get('cert_type', 'family')
        if cert_type not in ['family', 'volunteer']:
            cert_type = 'family'
        real_name = request.form.get('real_name', '').strip()[:50]
        id_card = request.form.get('id_card', '').strip()[:30]
        if not real_name or not id_card:
            flash('Real name, ID number, and a valid proof document are required.', 'error')
            return redirect(url_for('user_center.certification'))

        document_url = save_upload(
            request.files.get('document'), 'certifications', 'cert',
            allowed_exts=ALLOWED_DOC_EXTS
        )
        if not document_url:
            flash('Real name, ID number, and a valid proof document are required.', 'error')
            return redirect(url_for('user_center.certification'))

        diagnosis_date = None
        diagnosis_date_str = request.form.get('diagnosis_date', '').strip()
        if diagnosis_date_str:
            try:
                diagnosis_date = datetime.datetime.strptime(diagnosis_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        cert = Certification(
            user_id=current_user.id,
            cert_type=cert_type,
            real_name=real_name,
            id_card=id_card,
            relation=request.form.get('relation', '').strip()[:50],
            document_url=document_url,
            patient_name=request.form.get('patient_name', '').strip()[:50],
            patient_illness=request.form.get('patient_illness', '').strip()[:100],
            hospital_name=request.form.get('hospital_name', '').strip()[:100],
            diagnosis_date=diagnosis_date,
            status='pending'
        )

        additional_urls = []
        for i in range(1, 4):
            key = f'additional_doc_{i}'
            if key in request.files:
                url = save_upload(
                    request.files[key], 'certifications', 'cert_extra',
                    allowed_exts=ALLOWED_DOC_EXTS
                )
                if url:
                    additional_urls.append(url)
        if additional_urls:
            cert.additional_docs = json.dumps(additional_urls)

        db.session.add(cert)
        db.session.commit()
        flash('Certification application submitted! We will review it within 24-48 hours.', 'success')
        return redirect(url_for('user_center.certification'))
    return render_template('public/user/certification.html', cert=existing)


@user_center_bp.route('/certification/status')
@login_required
def certification_status():
    cert = Certification.query.filter_by(user_id=current_user.id).order_by(Certification.create_at.desc()).first()
    return render_template('public/user/certification_status.html', cert=cert)


@user_center_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'change_password':
            old_pw = request.form.get('old_password', '')
            new_pw = request.form.get('new_password', '')
            if not current_user.validate_password(old_pw):
                flash('Current password is incorrect.', 'error')
            elif len(new_pw) < 6:
                flash('New password must be at least 6 characters.', 'error')
            else:
                current_user.set_password(new_pw)
                db.session.commit()
                flash('Password changed successfully!', 'success')
        return redirect(url_for('user_center.settings'))
    return render_template('public/user/settings.html')


@user_center_bp.route('/history')
@login_required
def history():
    tab = request.args.get('tab', 'posts')
    if tab not in {'posts', 'campaigns', 'donations', 'requests'}:
        tab = 'posts'

    posts_page = request.args.get('posts_page', 1, type=int)
    campaigns_page = request.args.get('campaigns_page', 1, type=int)
    donations_page = request.args.get('donations_page', 1, type=int)
    requests_page = request.args.get('requests_page', 1, type=int)

    posts_query = Post.query.filter_by(user_id=current_user.id).filter(Post.delete_at.is_(None)).order_by(Post.create_at.desc())
    campaigns_query = Campaign.query.filter_by(user_id=current_user.id).order_by(Campaign.create_at.desc())
    donations_query = Donation.query.filter_by(user_id=current_user.id).order_by(Donation.create_at.desc())
    requests_query = RespiteRequest.query.filter_by(user_id=current_user.id).filter(RespiteRequest.delete_at.is_(None)).order_by(RespiteRequest.create_at.desc())

    posts = posts_query.paginate(page=posts_page, per_page=10, error_out=False)
    campaigns = campaigns_query.paginate(page=campaigns_page, per_page=10, error_out=False)
    donations = donations_query.paginate(page=donations_page, per_page=10, error_out=False)
    requests_list = requests_query.paginate(page=requests_page, per_page=10, error_out=False)

    return render_template(
        'public/user/history.html',
        tab=tab,
        posts=posts.items, campaigns=campaigns.items,
        donations=donations.items, requests=requests_list.items,
        posts_pagination=posts, campaigns_pagination=campaigns,
        donations_pagination=donations, requests_pagination=requests_list,
        post_count=posts.total, campaign_count=campaigns.total,
        donation_count=donations.total, request_count=requests_list.total
    )
