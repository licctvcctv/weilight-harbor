from flask import Blueprint

user_center_bp = Blueprint('user_center', __name__, url_prefix='/user')

from applications.view.user_center import routes
