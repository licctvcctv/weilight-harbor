from flask_login import LoginManager


def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login_page'
    login_manager.login_message = 'Please log in to access this page'

    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import flash, redirect, request, url_for
        from flask_babel import gettext as _

        flash(_('Please log in to access this page'), 'info')
        return redirect(url_for('auth.login_page', next=request.url))

    @login_manager.user_loader
    def load_user(user_id):
        from applications.models import User
        user = User.query.get(int(user_id))
        return user
