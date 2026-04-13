from flask import Blueprint

respite_bp = Blueprint('respite', __name__, url_prefix='/respite')

from applications.view.respite import routes
