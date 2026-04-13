from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

from applications.view.auth import routes
