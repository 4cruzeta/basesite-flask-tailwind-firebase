
import os
import json
import firebase_admin
from firebase_admin import credentials
from flask import Flask, g, request, redirect, url_for
from flask_babel import Babel
from google.cloud import secretmanager
from google.cloud import firestore
from werkzeug.middleware.proxy_fix import ProxyFix

# --- Global objects ---
db = None

# --- Function to access secrets ---
def get_secret(secret_id, version_id="latest"):
    """Fetches a secret from Google Cloud Secret Manager."""
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        print("Warning: GOOGLE_CLOUD_PROJECT environment variable not set.")
        return None

    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    try:
        response = client.access_secret_version(name=name)
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Could not fetch secret '{secret_id}' from project '{project_id}'. Error: {e}")
        return None

def create_app():
    """
    Application factory. Creates and configures the Flask application.
    """
    global db

    # --- App Initialization and Configuration ---
    app = Flask(__name__, template_folder='pages/templates', static_folder='static')

    # --- CRITICAL: PROXY FIX ---
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # --- Initialize Firebase Admin SDK ---
    try:
        firebase_creds_json = get_secret("firebase-credentials")
        if firebase_creds_json:
            firebase_creds = json.loads(firebase_creds_json)
            cred = credentials.Certificate(firebase_creds)
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK initialized successfully.")
        else:
            print("Could not initialize Firebase: credentials not found.")
    except Exception as e:
        print(f"Error initializing Firebase Admin SDK: {e}")

    # --- Initialize Firestore Client ---
    try:
        db = firestore.Client()
        print("Firestore client initialized successfully.")
    except Exception as e:
        db = None
        print(f"Error initializing Firestore client: {e}")

    # --- App Configuration ---
    app.config['SECRET_KEY'] = get_secret("website-secrets") or 'a_fallback_dev_secret_key'
    
    # --- THE LOGIN FIX: In a development environment (HTTP), this MUST be False. ---
    # In production (HTTPS), this should be True for security.
    is_prod = os.environ.get('GAE_ENV', '').startswith('standard')
    app.config['SESSION_COOKIE_SECURE'] = is_prod
    
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_NAME'] = '__session'
    
    # --- Language and Translation Config ---
    app.config['LANGUAGES'] = {'en_US': 'English', 'pt_BR': 'Português'}
    app.config['BABEL_DEFAULT_LOCALE'] = 'pt_BR'
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.path.join(basedir, 'translations')

    def get_locale():
        if g.get('lang_code') and g.lang_code in app.config['LANGUAGES']:
            return g.lang_code
        return request.accept_languages.best_match(app.config['LANGUAGES'].keys())

    Babel(app, locale_selector=get_locale)

    # --- Register Blueprints and Routes ---
    with app.app_context():
        from . import views
        from .whatsapp.routes import whatsapp_bp
        from .api.routes import api_bp
        from .web_client.routes import web_client_bp # <-- IMPORT THE NEW BLUEPRINT

        @app.before_request
        def set_lang_code():
            g.lang_code = request.view_args.get('lang_code') if request.view_args else None
            if g.lang_code not in app.config['LANGUAGES']:
                g.lang_code = None

        # Register Blueprints
        app.register_blueprint(views.views, url_prefix='/<lang_code>')
        app.register_blueprint(whatsapp_bp, url_prefix='/whatsapp')
        app.register_blueprint(api_bp, url_prefix='/api')
        app.register_blueprint(web_client_bp, url_prefix='/<lang_code>/client') # <-- REGISTER THE NEW BLUEPRINT
        
        @app.route('/')
        def root():
            # Redirect root to default language home
            default_lang = app.config.get('BABEL_DEFAULT_LOCALE', 'pt_BR')
            return redirect(url_for('views.home', lang_code=default_lang))

        from .util import inject_context_processors
        inject_context_processors(app)

    return app
