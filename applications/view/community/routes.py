import json
import random
import datetime
from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from applications.extensions import db
from applications.models.post import Post
from applications.models.comment import Comment
from applications.models.post_like import PostLike
from applications.models.confession import Confession
from applications.common.utils.files import save_multiple_uploads
from applications.common.utils.sensitive import check_sensitive, has_crisis_words
from applications.view.community import community_bp

COMMUNITY_CATEGORIES = [
    ('emotional', 'Emotional Support'),
    ('daily', 'Daily Life'),
    ('medical', 'Medical Info'),
    ('good_news', 'Good News'),
    ('resources', 'Resources'),
]


@community_bp.route('/')
def index():
    category = request.args.get('category', 'all')
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'latest')

    query = Post.query.options(joinedload(Post.user)).filter(
        Post.status == 1, Post.delete_at.is_(None)
    )
    if category != 'all':
        query = query.filter_by(category=category)
    if sort == 'hot':
        query = query.order_by((Post.like_count + Post.comment_count).desc())
    elif sort == 'empathy':
        query = query.order_by(Post.like_count.desc())
    else:
        query = query.order_by(Post.create_at.desc())

    pagination = query.paginate(page=page, per_page=15, error_out=False)
    confessions = Confession.query.order_by(Confession.create_at.desc()).limit(10).all()

    categories_with_all = [('all', 'All')] + COMMUNITY_CATEGORIES

    return render_template('public/community/index.html',
                           posts=pagination.items, pagination=pagination,
                           categories=categories_with_all, current_category=category,
                           current_sort=sort, confessions=confessions)


@community_bp.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.options(joinedload(Post.user)).get_or_404(post_id)
    if post.delete_at is not None:
        flash('This post is no longer available.', 'error')
        return redirect(url_for('community.index'))
    if post.status != 1 and (not current_user.is_authenticated or post.user_id != current_user.id):
        flash('This post is no longer available.', 'error')
        return redirect(url_for('community.index'))

    post.view_count += 1
    db.session.commit()

    comments = Comment.query.options(
        joinedload(Comment.user),
        joinedload(Comment.parent).joinedload(Comment.user),
    ).filter_by(
        post_id=post_id
    ).filter(Comment.delete_at.is_(None)).order_by(Comment.create_at.asc()).all()

    user_liked = False
    if current_user.is_authenticated:
        user_liked = db.session.query(
            PostLike.query.filter_by(post_id=post_id, user_id=current_user.id).exists()
        ).scalar()

    return render_template('public/community/post_detail.html',
                           post=post, comments=comments, user_liked=user_liked)


@community_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category = request.form.get('category', 'daily')
        is_anonymous = request.form.get('is_anonymous') == 'on'

        if not title or not content:
            flash('Title and content are required.', 'error')
            return render_template('public/community/create_post.html',
                                   categories=COMMUNITY_CATEGORIES)

        images = save_multiple_uploads(
            request.files.getlist('images'), 'posts', 'post'
        )

        post = Post(
            user_id=current_user.id, title=title, content=content,
            category=category,
            images=json.dumps(images) if images else None,
            is_anonymous=is_anonymous
        )
        db.session.add(post)
        db.session.commit()

        # Check for sensitive words in title + content
        sensitive_matches = check_sensitive(title + ' ' + content)
        if any(m['severity'] >= 1 for m in sensitive_matches):
            post.status = 0  # hidden, pending review
            db.session.commit()
            flash('Your post has been submitted and is pending review due to content moderation.', 'warning')
        else:
            flash('Post published successfully!', 'success')

        return redirect(url_for('community.post_detail', post_id=post.id))

    return render_template('public/community/create_post.html',
                           categories=COMMUNITY_CATEGORIES)


@community_bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def toggle_like(post_id):
    post = Post.query.get_or_404(post_id)
    existing = PostLike.query.filter_by(
        post_id=post_id, user_id=current_user.id
    ).first()
    if existing:
        db.session.delete(existing)
        post.like_count = max(0, post.like_count - 1)
        liked = False
    else:
        db.session.add(PostLike(post_id=post_id, user_id=current_user.id))
        post.like_count += 1
        liked = True
    db.session.commit()
    return jsonify({'liked': liked, 'count': post.like_count})


@community_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form.get('content', '').strip()
    parent_id = request.form.get('parent_id', type=int)

    if not content:
        flash('Comment cannot be empty.', 'error')
        return redirect(url_for('community.post_detail', post_id=post_id))

    db.session.add(Comment(
        post_id=post_id, user_id=current_user.id,
        content=content, parent_id=parent_id
    ))
    post.comment_count += 1
    db.session.commit()
    flash('Comment added!', 'success')
    return redirect(url_for('community.post_detail', post_id=post_id))


@community_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        flash('You can only delete your own posts.', 'error')
        return redirect(url_for('community.index'))
    post.delete_at = datetime.datetime.now()
    post.status = 0
    db.session.commit()
    flash('Post deleted.', 'success')
    return redirect(url_for('community.index'))


# --- Night Confessions ---

@community_bp.route('/confessions', methods=['GET'])
def confessions_api():
    page = request.args.get('page', 1, type=int)
    confessions = Confession.query.order_by(
        Confession.create_at.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    return jsonify({
        'confessions': [{
            'id': c.id, 'content': c.content, 'nickname': c.nickname,
            'hug_count': c.hug_count,
            'create_at': c.create_at.strftime('%Y-%m-%d %H:%M') if c.create_at else ''
        } for c in confessions.items],
        'has_next': confessions.has_next
    })


@community_bp.route('/confessions', methods=['POST'])
def post_confession():
    data = request.get_json(silent=True) or {}
    content = data.get('content', '').strip()
    session_id = data.get('session_id', '')

    if not content:
        return jsonify({'error': 'Content is required'}), 400

    if has_crisis_words(content):
        return jsonify({
            'crisis': True,
            'message': 'We noticed your words may reflect a difficult moment.'
        })

    animals = ['Firefly', 'Starling', 'Moonbird', 'Dewdrop',
               'Glowworm', 'Nightingale', 'Snowflake', 'Raindrop']
    nickname = f"Anonymous {random.choice(animals)} #{random.randint(1000, 9999)}"

    confession = Confession(content=content, nickname=nickname, session_id=session_id)
    db.session.add(confession)
    db.session.commit()
    return jsonify({
        'id': confession.id, 'content': confession.content,
        'nickname': confession.nickname, 'hug_count': 0,
        'create_at': confession.create_at.strftime('%Y-%m-%d %H:%M')
    })


@community_bp.route('/confessions/<int:confession_id>/hug', methods=['POST'])
def hug_confession(confession_id):
    confession = Confession.query.get_or_404(confession_id)
    confession.hug_count += 1
    db.session.commit()
    return jsonify({'hug_count': confession.hug_count})


@community_bp.route('/check-sensitive', methods=['POST'])
def check_sensitive_api():
    data = request.get_json(silent=True) or {}
    text = data.get('text', '')
    matches = check_sensitive(text)
    return jsonify({
        'matches': matches,
        'has_crisis': any(m['severity'] >= 2 for m in matches)
    })
