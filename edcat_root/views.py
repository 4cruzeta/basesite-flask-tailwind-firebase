
from flask import Blueprint, render_template, current_app, request, jsonify, redirect, url_for, g
from firebase_admin import auth
import functools

views = Blueprint('views', __name__)

def login_required(view):
    """
    View decorator that verifies the __session cookie on each request.
    This is the only cookie-based approach compatible with Firebase Hosting's CDN.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        lang_code = kwargs.get('lang_code', 'pt_BR')
        id_token = request.cookies.get('__session')

        if not id_token:
            return redirect(url_for('views.login', lang_code=lang_code))

        try:
            decoded_token = auth.verify_id_token(id_token)
            g.user = decoded_token
        except Exception:
            return redirect(url_for('views.login', lang_code=lang_code))

        return view(**kwargs)
    return wrapped_view

# --- Public Routes ---

@views.route('/home')
def home(lang_code):
    return render_template("index.html")

@views.route('/login', methods=['GET'])
def login(lang_code):
    firebase_config = current_app.config.get('FIREBASE_CLIENT_CONFIG')
    return render_template("login.html", firebase_config=firebase_config)

# --- Authentication Handling ---

@views.route('/session_login', methods=['POST'])
def session_login(lang_code):
    try:
        id_token = request.json.get('token')
        auth.verify_id_token(id_token, check_revoked=True)
        
        response = jsonify({"status": "success"})
        response.set_cookie(
            '__session', 
            id_token, 
            httponly=True, 
            secure=True, 
            samesite='Lax'
        )
        return response
    except Exception as e:
        return jsonify({"status": "error", "message": f"An unexpected error occurred: {e}"}), 500

@views.route("/logout")
def logout(lang_code):
    response = redirect(url_for('views.home', lang_code=lang_code))
    response.set_cookie('__session', '', expires=0)
    return response

# --- Protected Routes ---

@views.route("/admin_home")
@login_required
def admin_home(lang_code):
    return render_template("admin_home.html", email=g.user.get('email'))
