import datetime
from functools import wraps
from flask import Blueprint, abort, jsonify, render_template, request
from flask_babel import gettext as _
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload
from applications.extensions import db
from applications.models.post import Post
from applications.common.utils.http import success_api, fail_api, table_api

admin_community = Blueprint('adminCommunity', __name__, url_prefix='/admin/community')


def admin_required(func):
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if getattr(current_user, 'user_type', None) != 'admin':
            if request.method != 'GET' or request.path.endswith('/data'):
                return jsonify({'success': False, 'msg': _('Permission denied')}), 403
            abort(403)
        return func(*args, **kwargs)
    return wrapper


@admin_community.get('/')
@admin_required
def main():
    return render_template('admin/community/main.html')


@admin_community.get('/data')
@admin_required
def data():
    status_filter = request.args.get('status', '')
    query = Post.query.options(joinedload(Post.user))
    if status_filter != '':
        query = query.filter_by(status=int(status_filter))
    query = query.filter(Post.delete_at.is_(None)).order_by(Post.create_at.desc())
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    result = []
    for p in pagination.items:
        result.append({
            'id': p.id, 'username': p.user.username if p.user else '',
            'title': p.title, 'category': p.category,
            'content': (p.content or '')[:100], 'status': p.status,
            'is_anonymous': p.is_anonymous, 'like_count': p.like_count,
            'comment_count': p.comment_count,
            'create_at': p.create_at.strftime('%Y-%m-%d %H:%M') if p.create_at else ''
        })
    return table_api(data=result, count=pagination.total)


@admin_community.put('/approve/<int:post_id>')
@admin_required
def approve(post_id):
    post = Post.query.get(post_id)
    if not post:
        return fail_api(msg=_("Not found"))
    post.status = 1
    db.session.commit()
    return success_api(msg=_("Post approved"))


@admin_community.put('/hide/<int:post_id>')
@admin_required
def hide(post_id):
    post = Post.query.get(post_id)
    if not post:
        return fail_api(msg=_("Not found"))
    post.status = 0
    db.session.commit()
    return success_api(msg=_("Post hidden"))


@admin_community.delete('/delete/<int:post_id>')
@admin_required
def delete(post_id):
    post = Post.query.get(post_id)
    if not post:
        return fail_api(msg=_("Not found"))
    post.delete_at = datetime.datetime.now()
    post.status = 0
    db.session.commit()
    return success_api(msg=_("Post deleted"))
