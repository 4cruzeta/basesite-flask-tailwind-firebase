
import os
import json
import firebase_admin
from firebase_admin import credentials, auth
from flask import Flask, request, g, redirect, url_for, session, jsonify
from flask_babel import Babel, gettext as _
from views import views
from google.cloud import secretmanager
from werkzeug.middleware.proxy_fix import ProxyFix # Import ProxyFix

# --- Function to access secrets ---
def get_secret(secret_id, version_id="latest"):
    """Fetches a secret from Google Cloud Secret Manager, dynamically detecting the project ID."""
    project_id = None  # Initialize project_id to improve error logging
    try:
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            project_id = "290529487715"

        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(name=name)
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Could not fetch secret '{secret_id}' from project '{project_id}'. Error: {e}")
        return None

# --- Firebase Admin Initialization ---
def initialize_firebase():
    """Initializes the Firebase Admin SDK."""
    try:
        firebase_creds_json = get_secret("firebase-credentials")
        if firebase_creds_json:
            firebase_creds = json.loads(firebase_creds_json)
            cred = credentials.Certificate(firebase_creds)
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK initialized successfully.")
        else:
            print("Could not initialize Firebase: credentials not found in Secret Manager.")
    except Exception as e:
        print(f"Error initializing Firebase Admin SDK: {e}")


# --- App Initialization and Configuration --
app = Flask(__name__, template_folder='pages/templates', static_folder='static')

# --- CRITICAL: PROXY FIX ---
# This tells Flask to trust the headers sent by the proxy (like Cloud Run)
# about the original request being secure (HTTPS). This is essential for secure cookies to work.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Initialize Firebase
initialize_firebase()

# --- Secret and Language Configuration ---
app.config['SECRET_KEY'] = get_secret("website-secrets") or 'dev_secret_key_for_session_stability'

# Enforce Secure Cookies for Production
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Fetch Firebase client config
app.config['FIREBASE_CLIENT_CONFIG'] = {
    "apiKey": get_secret("FIREBASE_API_KEY"),
    "authDomain": get_secret("FIREBASE_AUTH_DOMAIN"),
    "projectId": get_secret("FIREBASE_PROJECT_ID"),
    "storageBucket": get_secret("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": get_secret("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": get_secret("FIREBASE_APP_ID")
}

app.config['LANGUAGES'] = {'en_US': 'English', 'pt_BR': 'Português'}
app.config['BABEL_DEFAULT_LOCALE'] = 'pt_BR'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.path.join(basedir, 'translations')

# --- Babel Initialization ---
def get_locale():
    if g.get('lang_code') and g.lang_code in app.config['LANGUAGES']:
        return g.lang_code
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys())

babel = Babel(app, locale_selector=get_locale)

# --- Request Handlers ---
@app.before_request
def set_lang_code():
    # Defensive check: Ensure view_args exists before accessing it.
    # This prevents crashes on requests like /favicon.ico that have no route.
    if request.view_args and 'lang_code' in request.view_args and request.view_args['lang_code'] in app.config['LANGUAGES']:
        g.lang_code = request.view_args['lang_code']
    else:
        g.lang_code = None

@app.route('/')
def root_redirect():
    lang_code = request.accept_languages.best_match(app.config['LANGUAGES'].keys()) or app.config['BABEL_DEFAULT_LOCALE']
    return redirect(url_for('views.home', lang_code=lang_code))

# --- Register Blueprints ---
app.register_blueprint(views, url_prefix='/<lang_code>')

# --- Template Context Processors ---
@app.context_processor
def inject_language_switcher():
    """
    Injects a function into templates to generate URLs for the current
    page in a different language. This maintains the user's current page
    when they switch languages.
    """
    def change_lang_url(lang_code):
        if request.endpoint and request.view_args:
            view_args = request.view_args.copy()
            view_args['lang_code'] = lang_code
            try:
                return url_for(request.endpoint, **view_args)
            except:
                # Fallback if URL building fails for any reason
                return url_for('views.home', lang_code=lang_code)
        # Fallback for pages without a clear endpoint (like 404)
        return url_for('views.home', lang_code=lang_code)

    return dict(change_lang_url=change_lang_url)

@app.context_processor
def inject_gettext():
    return dict(_=_)

# --- Main Execution ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
