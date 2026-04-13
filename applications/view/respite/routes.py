import datetime
from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from applications.extensions import db
from applications.models.respite_request import RespiteRequest
from applications.view.respite import respite_bp


@respite_bp.route('/')
def index():
    return render_template('public/respite/index.html')


@respite_bp.route('/requests')
def requests_api():
    """Return all active requests as JSON for map pins."""
    req_type = request.args.get('type', 'all')  # all, service, equipment
    query = RespiteRequest.query.options(joinedload(RespiteRequest.user)).filter(
        RespiteRequest.status.in_(['pending', 'in_progress']),
        RespiteRequest.delete_at.is_(None)
    )
    if req_type == 'service':
        query = query.filter_by(request_type='service')
    elif req_type == 'equipment':
        query = query.filter_by(request_type='equipment')

    items = query.order_by(RespiteRequest.create_at.desc()).limit(500).all()
    result = []
    for r in items:
        result.append({
            'id': r.id,
            'title': r.title,
            'description': (r.description or '')[:100],
            'request_type': r.request_type,
            'category': r.category,
            'city': r.city or '',
            'district': r.district or '',
            'latitude': r.latitude,
            'longitude': r.longitude,
            'pin_color': 'orange' if r.request_type == 'service' else 'green',
            'status': r.status,
            'time_limit': r.time_limit or '',
            'username': r.user.username if r.user else 'Unknown',
            'is_certified': r.user.is_certified if r.user else False,
            'create_at': r.create_at.strftime('%Y-%m-%d %H:%M') if r.create_at else ''
        })
    return jsonify({'requests': result})


@respite_bp.route('/request/<int:req_id>')
def request_detail(req_id):
    """Return single request detail as JSON for InfoWindow."""
    r = RespiteRequest.query.get_or_404(req_id)
    return jsonify({
        'id': r.id,
        'title': r.title,
        'description': r.description,
        'request_type': r.request_type,
        'category': r.category,
        'address': r.address or '',
        'city': r.city or '',
        'time_limit': r.time_limit or '',
        'status': r.status,
        'username': r.user.username if r.user else 'Unknown',
        'is_certified': r.user.is_certified if r.user else False,
        'user_id': r.user_id,
        'create_at': r.create_at.strftime('%Y-%m-%d %H:%M') if r.create_at else ''
    })


@respite_bp.route('/create', methods=['POST'])
@login_required
def create_request():
    if not current_user.is_certified:
        return jsonify({'error': 'Only certified users can create requests.'}), 403

    data = request.get_json(silent=True) or {}
    req = RespiteRequest(
        user_id=current_user.id,
        request_type=data.get('request_type', 'service'),
        title=data.get('title', '').strip(),
        description=data.get('description', '').strip(),
        category=data.get('category', ''),
        province=data.get('province', ''),
        city=data.get('city', ''),
        district=data.get('district', ''),
        address=data.get('address', ''),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        pin_color='orange' if data.get('request_type') == 'service' else 'green',
        time_limit=data.get('time_limit', ''),
        status='pending'
    )
    if not req.title:
        return jsonify({'error': 'Title is required.'}), 400
    db.session.add(req)
    db.session.commit()
    return jsonify({'success': True, 'id': req.id})


@respite_bp.route('/request/<int:req_id>/accept', methods=['POST'])
@login_required
def accept_request(req_id):
    if not current_user.is_certified:
        return jsonify({'error': 'Only certified users can accept requests.'}), 403

    req = RespiteRequest.query.get_or_404(req_id)
    if req.status != 'pending':
        return jsonify({'error': 'This request is no longer available.'}), 400
    if req.user_id == current_user.id:
        return jsonify({'error': 'You cannot accept your own request.'}), 400

    req.acceptor_id = current_user.id
    req.accepted_at = datetime.datetime.now()
    req.status = 'in_progress'
    db.session.commit()
    return jsonify({'success': True})


@respite_bp.route('/request/<int:req_id>/complete', methods=['POST'])
@login_required
def complete_request(req_id):
    req = RespiteRequest.query.get_or_404(req_id)
    if req.user_id != current_user.id:
        return jsonify({'error': 'Only the requester can mark as completed.'}), 403
    req.status = 'completed'
    req.completed_at = datetime.datetime.now()
    db.session.commit()
    return jsonify({'success': True})
