import os
from flask import Flask, request, session, redirect, url_for
from flask_babel import Babel
from .views import views # Import views from the local package

# This function is called by Babel to determine which language to use.
# It checks for a language choice in the user's session first.
def get_locale():
    if 'language' in session:
        return session['language']
    return request.accept_languages.best_match(['en_US', 'pt_BR'])

# Create and configure the Flask app instance
app = Flask(__name__, template_folder='pages/templates', static_folder='static')
app.config['SECRET_KEY'] = 'dev_secret_key_for_session_stability'
app.config['LANGUAGES'] = ['en_US', 'pt_BR']

# Initialize Babel
babel = Babel(app,
              locale_selector=get_locale,
              default_translation_directories='translations')

# Register the blueprint for your pages
app.register_blueprint(views, url_prefix='/')

# Route to set the user's language choice in the session.
@app.route('/language/<lang>')
def set_language(lang=None):
    session['language'] = lang
    return redirect(request.referrer or url_for('views.home'))

# This block runs the app in a development server.
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
