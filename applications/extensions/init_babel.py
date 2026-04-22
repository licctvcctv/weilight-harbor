from flask import session, request
from flask_babel import Babel

babel = Babel()


def get_locale():
    if 'locale' in session:
        return session['locale']
    try:
        from flask_login import current_user
        if current_user.is_authenticated and current_user.locale:
            return current_user.locale
    except Exception:
        pass
    cookie_locale = request.cookies.get('locale')
    if cookie_locale in ['en', 'zh']:
        return cookie_locale
    return request.accept_languages.best_match(['en', 'zh'], default='en')


def init_babel(app):
    babel.init_app(app, locale_selector=get_locale)

    @app.context_processor
    def inject_locale():
        return dict(get_locale=get_locale)
