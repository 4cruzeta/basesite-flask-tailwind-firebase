
from flask import Flask, request, session, redirect, url_for
from flask_babel import Babel
import os

# This function is called by Babel to determine which language to use.
# It checks for a language choice in the user's session first.
def get_locale():
    if 'language' in session:
        return session['language']
    return request.accept_languages.best_match(['en_US', 'pt_BR'])

def create_app():
    # Create the Flask app instance
    app = Flask(__name__, template_folder='pages/templates', static_folder='static')

    # Set a static secret key to maintain sessions across server reloads.
    app.config['SECRET_KEY'] = 'dev_secret_key_for_session_stability'
    app.config['LANGUAGES'] = ['en_US', 'pt_BR']

    # Initialize Babel correctly using the corrected keyword argument as per the error message.
    babel = Babel(app, 
                  locale_selector=get_locale, 
                  default_translation_directories='translations')

    # Route to set the user's language choice in the session.
    @app.route('/language/<lang>')
    def set_language(lang=None):
        session['language'] = lang
        return redirect(request.referrer or url_for('views.home'))

    # Import and register the main blueprint for your pages.
    from .views import views
    app.register_blueprint(views, url_prefix='/')

    return app
