from flask import Blueprint

community_bp = Blueprint('community', __name__, url_prefix='/community')

from applications.view.community import routes
