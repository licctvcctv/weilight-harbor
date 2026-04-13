from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from applications.extensions import db
from applications.models import User, Role
from applications.view.auth import auth_bp


@auth_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user is None and '@' in username:
            user = User.query.filter_by(email=username).first()
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
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('public/auth/register.html')
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('public/auth/register.html')
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'error')
            return render_template('public/auth/register.html')

        user = User(username=username, email=email, enable=1, user_type='regular')
        user.set_password(password)
        regular_role = Role.query.filter_by(code='regular').first()
        if regular_role:
            user.role.append(regular_role)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Welcome to Weilight Harbor!', 'success')
        return redirect('/')
    return render_template('public/auth/register.html')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if email:
            flash('If an account exists with this email, a reset link has been sent. (Demo mode)', 'success')
        return redirect(url_for('auth.login_page'))
    return render_template('public/auth/forgot_password.html')


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    session.pop('permissions', None)
    return redirect('/')
