from flask import Blueprint

crowdfunding_bp = Blueprint('crowdfunding', __name__, url_prefix='/crowdfunding')

from applications.view.crowdfunding import routes
