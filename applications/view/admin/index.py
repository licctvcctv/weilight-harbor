from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

from applications.common.utils.rights import authorize
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# 登录页
@admin_bp.get('/login')
def login():
    if current_user.is_authenticated and current_user.user_type == 'admin':
        return redirect(url_for('admin.index'))
    return render_template('admin/login.html')


# 首页
@admin_bp.get('/')
@authorize("admin:review", log=True)
def index():
    user = current_user
    return render_template('admin/index.html', user=user)


# 控制台页面
@admin_bp.get('/welcome')
@authorize("admin:review", log=True)
def welcome():
    return redirect(url_for('adminCert.main'))
