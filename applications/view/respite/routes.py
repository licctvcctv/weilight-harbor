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
    is_requester = current_user.is_authenticated and current_user.id == r.user_id
    is_acceptor = current_user.is_authenticated and current_user.id == r.acceptor_id

    data = {
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
        'acceptor_id': r.acceptor_id,
        'acceptor_username': r.acceptor.username if r.acceptor else '',
        'accepted_at': r.accepted_at.strftime('%Y-%m-%d %H:%M') if r.accepted_at else '',
        'is_requester': is_requester,
        'is_acceptor': is_acceptor,
        'can_complete': is_requester and r.status == 'in_progress',
        'create_at': r.create_at.strftime('%Y-%m-%d %H:%M') if r.create_at else ''
    }
    if is_requester and r.acceptor:
        data['acceptor_contact'] = {
            'username': r.acceptor.username,
            'phone': r.acceptor.phone or '',
            'email': r.acceptor.email or ''
        }
    if is_acceptor and r.user:
        data['requester_contact'] = {
            'username': r.user.username,
            'phone': r.user.phone or '',
            'email': r.user.email or ''
        }
    return jsonify(data)


@respite_bp.route('/create', methods=['POST'])
@login_required
def create_request():
    if not current_user.is_certified:
        return jsonify({'error': 'Only certified users can create requests.'}), 403

    data = request.get_json(silent=True) or {}
    request_type = data.get('request_type', 'service')
    if request_type not in ['service', 'equipment']:
        return jsonify({'error': 'Invalid request type.'}), 400

    try:
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
    except (TypeError, ValueError):
        return jsonify({'error': 'A valid map location is required.'}), 400

    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return jsonify({'error': 'A valid map location is required.'}), 400

    title = (data.get('title') or '').strip()[:200]
    description = (data.get('description') or '').strip()[:2000]
    req = RespiteRequest(
        user_id=current_user.id,
        request_type=request_type,
        title=title,
        description=description,
        category=(data.get('category') or '')[:50],
        province=(data.get('province') or '')[:50],
        city=(data.get('city') or '')[:50],
        district=(data.get('district') or '')[:50],
        address=(data.get('address') or '')[:255],
        latitude=latitude,
        longitude=longitude,
        pin_color='orange' if request_type == 'service' else 'green',
        time_limit=(data.get('time_limit') or '')[:100],
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
    return jsonify({
        'success': True,
        'requester_contact': {
            'username': req.user.username if req.user else '',
            'phone': req.user.phone if req.user else '',
            'email': req.user.email if req.user else ''
        }
    })


@respite_bp.route('/request/<int:req_id>/complete', methods=['POST'])
@login_required
def complete_request(req_id):
    req = RespiteRequest.query.get_or_404(req_id)
    if req.user_id != current_user.id:
        return jsonify({'error': 'Only the requester can mark as completed.'}), 403
    if req.status != 'in_progress':
        return jsonify({'error': 'Only accepted requests can be marked as completed.'}), 400
    req.status = 'completed'
    req.completed_at = datetime.datetime.now()
    db.session.commit()
    return jsonify({'success': True})
