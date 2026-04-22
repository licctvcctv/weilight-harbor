import random
import re
import time

from flask import render_template, request, redirect, url_for, flash, session, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from applications.extensions import db
from applications.models import User, Role
from applications.view.auth import auth_bp

PHONE_CODE_TTL_SECONDS = 10 * 60
PHONE_CODE_RESEND_SECONDS = 60


def _normalize_phone(phone):
    phone = (phone or '').strip()
    if phone.startswith('+'):
        return '+' + re.sub(r'\D', '', phone[1:])
    return re.sub(r'\D', '', phone)


def _is_valid_phone(phone):
    return bool(re.fullmatch(r'\+?\d{6,20}', phone or ''))


def _phone_code_record():
    return session.get('phone_verification') or {}


def _verify_phone_code(phone, code):
    record = _phone_code_record()
    if not record:
        return False
    if record.get('phone') != phone:
        return False
    if record.get('code') != (code or '').strip():
        return False
    return float(record.get('expires_at', 0)) >= time.time()


@auth_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        username = request.form.get('username', '').strip()[:120]
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user is None and '@' in username:
            user = User.query.filter_by(email=username).first()
        if user is None:
            user = User.query.filter_by(phone=_normalize_phone(username)).first()
        if user and user.validate_password(password):
            if user.enable == 0:
                flash('Account is disabled.', 'error')
                return render_template('public/auth/login.html')
            login_user(user)
            from applications.common.admin import add_auth_session
            add_auth_session()
            next_url = request.args.get('next', '/')
            return redirect(next_url)
        flash('Invalid username or password.', 'error')
    return render_template('public/auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register_page():
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        username = request.form.get('username', '').strip()[:20]
        email = request.form.get('email', '').strip()[:120]
        phone = _normalize_phone(request.form.get('phone', ''))
        verification_code = request.form.get('verification_code', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not username or not email or not phone or not password:
            flash('All fields are required.', 'error')
            return render_template('public/auth/register.html')
        if not _is_valid_phone(phone):
            flash('Please enter a valid phone number.', 'error')
            return render_template('public/auth/register.html')
        if not _verify_phone_code(phone, verification_code):
            flash('Invalid or expired phone verification code.', 'error')
            return render_template('public/auth/register.html')
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('public/auth/register.html')
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'error')
            return render_template('public/auth/register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('public/auth/register.html')
        if User.query.filter_by(phone=phone).first():
            flash('Phone number already registered.', 'error')
            return render_template('public/auth/register.html')

        user = User(username=username, email=email, phone=phone, enable=1, user_type='regular')
        user.set_password(password)
        regular_role = Role.query.filter_by(code='regular').first()
        if regular_role:
            user.role.append(regular_role)
        db.session.add(user)
        db.session.commit()
        session.pop('phone_verification', None)
        login_user(user)
        flash('Welcome to Weilight Harbor!', 'success')
        return redirect('/')
    return render_template('public/auth/register.html')


@auth_bp.route('/send-phone-code', methods=['POST'])
def send_phone_code():
    data = request.get_json(silent=True) or request.form
    phone = _normalize_phone(data.get('phone', ''))
    if not _is_valid_phone(phone):
        return jsonify({'success': False, 'error': 'Please enter a valid phone number.'}), 400

    record = _phone_code_record()
    last_sent_at = float(record.get('sent_at', 0) or 0)
    remaining = int(PHONE_CODE_RESEND_SECONDS - (time.time() - last_sent_at))
    if remaining > 0 and record.get('phone') == phone:
        return jsonify({
            'success': False,
            'error': f'Please wait {remaining} seconds before requesting another code.'
        }), 429

    code = f'{random.randint(0, 999999):06d}'
    session['phone_verification'] = {
        'phone': phone,
        'code': code,
        'sent_at': time.time(),
        'expires_at': time.time() + PHONE_CODE_TTL_SECONDS
    }
    response = {
        'success': True,
        'message': 'Verification code sent.'
    }
    if current_app.config.get('PHONE_CODE_DEV_MODE'):
        response['dev_code'] = code
    return jsonify(response)


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        account = request.form.get('account', '').strip()[:120]
        phone = _normalize_phone(request.form.get('phone', ''))
        verification_code = request.form.get('verification_code', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        user = User.query.filter_by(username=account).first()
        if user is None and '@' in account:
            user = User.query.filter_by(email=account).first()

        if not account or not phone or not verification_code or not password:
            flash('All fields are required.', 'error')
            return render_template('public/auth/forgot_password.html')
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('public/auth/forgot_password.html')
        if not user or user.phone != phone or not _verify_phone_code(phone, verification_code):
            flash('Account information or verification code is invalid.', 'error')
            return render_template('public/auth/forgot_password.html')

        user.set_password(password)
        db.session.commit()
        session.pop('phone_verification', None)
        flash('Password reset successfully. Please log in with your new password.', 'success')
        return redirect(url_for('auth.login_page'))
    return render_template('public/auth/forgot_password.html')


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    session.pop('permissions', None)
    return redirect('/')
