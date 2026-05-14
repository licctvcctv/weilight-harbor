from functools import wraps
from flask import abort, request, jsonify, session
from flask_login import login_required, current_user
from applications.common.admin_log import admin_log


def _current_permissions():
    permissions = set(session.get('permissions', []))
    if current_user.is_authenticated:
        for role in current_user.role:
            if role.enable == 0:
                continue
            for power in role.power:
                if power.enable == 0:
                    continue
                permissions.add(power.code)
    return permissions


def authorize(power: str, log: bool = False):
    def decorator(func):
        @login_required
        @wraps(func)
        def wrapper(*args, **kwargs):
            if power not in _current_permissions():
                if log:
                    admin_log(request=request, is_access=False)
                if request.method == 'GET':
                    abort(403)
                else:
                    return jsonify(success=False, msg="权限不足!")
            if log:
                admin_log(request=request, is_access=True)
            return func(*args, **kwargs)

        return wrapper

    return decorator
