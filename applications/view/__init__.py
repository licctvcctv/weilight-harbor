from applications.view.admin import register_admin_views
from applications.view.index import register_index_views
from applications.view.passport import register_passport_views
from applications.view.rights import register_rights_view
from applications.view.department import register_dept_views
from applications.view.auth import auth_bp
from applications.view.user_center import user_center_bp
from applications.view.community import community_bp
from applications.view.crowdfunding import crowdfunding_bp
from applications.view.journal import journal_bp
from applications.view.respite import respite_bp


def init_view(app):
    register_admin_views(app)
    register_index_views(app)
    register_rights_view(app)
    register_passport_views(app)
    register_dept_views(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_center_bp)
    app.register_blueprint(community_bp)
    app.register_blueprint(crowdfunding_bp)
    app.register_blueprint(journal_bp)
    app.register_blueprint(respite_bp)
