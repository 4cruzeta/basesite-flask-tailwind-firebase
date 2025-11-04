
import json
from flask import Blueprint, render_template, current_app, request, jsonify, redirect, url_for, g
from firebase_admin import auth
import functools
from datetime import datetime

# Import shared objects from the application factory
from edcat_root import db, get_secret

views = Blueprint('views', __name__)


def login_required(view):
    """Decorator that verifies session, syncs roles, and prepares user data."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        lang_code = kwargs.get('lang_code', 'pt_BR')
        id_token = request.cookies.get('__session')

        if not id_token:
            return redirect(url_for('views.login', lang_code=lang_code))

        try:
            decoded_token = auth.verify_id_token(id_token)
            g.user = decoded_token
            uid = g.user['uid']
            email = g.user.get('email')

            admin_emails_str = get_secret('ADMIN_USERS')
            admin_emails = [e.strip() for e in admin_emails_str.split(',')] if admin_emails_str else []
            is_admin_by_secret = email in admin_emails

            role_to_set = 'admin' if is_admin_by_secret else 'user'
            g.user_role = role_to_set

            if db:
                user_ref = db.collection('users').document(uid)
                user_doc = user_ref.get()
                current_role = user_doc.to_dict().get('role') if user_doc.exists else None

                if current_role != role_to_set:
                    user_ref.set({'role': role_to_set}, merge=True)
            
        except Exception as e:
            print(f"Error in login_required decorator: {e}")
            # Clear bad cookie and redirect to login
            response = redirect(url_for('views.login', lang_code=lang_code))
            response.set_cookie('__session', '', expires=0)
            return response

        return view(**kwargs)
    return wrapped_view


def admin_required(view):
    """Decorator that checks if the user has the 'admin' role assigned in the g object."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if getattr(g, 'user_role', 'user') != 'admin':
            lang_code = kwargs.get('lang_code', 'pt_BR')
            return redirect(url_for('views.home', lang_code=lang_code))
        return view(**kwargs)
    return wrapped_view

# --- Public Routes ---

@views.route('/home')
def home(lang_code):
    return render_template("index.html")

@views.route('/login', methods=['GET'])
def login(lang_code):
    firebase_config_json = get_secret("firebase-client-config")
    firebase_config = json.loads(firebase_config_json) if firebase_config_json else {}
    return render_template("login.html", firebase_config=firebase_config)

# --- Authentication Handling ---

@views.route('/session_login', methods=['POST'])
def session_login(lang_code):
    try:
        id_token = request.json['token']
        decoded_token = auth.verify_id_token(id_token, check_revoked=True)
        uid = decoded_token['uid']

        if db:
            user_ref = db.collection('users').document(uid)
            # Ensure a user document exists and set last login
            user_ref.set({
                'email': decoded_token.get('email'),
                'last_login_timestamp': datetime.utcnow()
            }, merge=True)

        response = jsonify({"status": "success"})
        # Use app config for cookie settings
        secure_cookie = current_app.config.get('SESSION_COOKIE_SECURE', True)
        response.set_cookie('__session', id_token, httponly=True, secure=secure_cookie, samesite='Lax')
        return response
    except Exception as e:
        print(f"Error during session login: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@views.route("/logout")
def logout(lang_code):
    # Redirect to home in the current language
    response = redirect(url_for('views.home', lang_code=lang_code))
    response.set_cookie('__session', '', expires=0)
    return response

# --- Protected Admin Routes ---

@views.route("/admin_home")
@login_required
@admin_required
def admin_home(lang_code):
    users_list = []
    if db:
        try:
            users_ref = db.collection('users').stream()
            for user in users_ref:
                user_data = user.to_dict()
                user_data['uid'] = user.id
                users_list.append(user_data)
        except Exception as e:
            print(f"Error fetching users: {e}")
            
    return render_template("admin_home.html", email=g.user.get('email'), users=users_list)

@views.route("/create_user", methods=['POST'])
@login_required
@admin_required
def create_user(lang_code):
    if not db:
        return redirect(url_for('views.admin_home', lang_code=lang_code))
        
    try:
        full_name = request.form['fullName']
        email = request.form['email']
        password = request.form['password']
        raga_access = 'RAGA' in request.form.getlist('services')

        new_user_auth = auth.create_user(email=email, password=password, display_name=full_name)

        subscribed_services = ['RAGA'] if raga_access else []
        
        # New users are always created with the 'user' role by default.
        # The login_required decorator will promote them to admin on their first login
        # if their email is in the ADMIN_USERS secret.
        user_data = {
            'uid': new_user_auth.uid,
            'email': email,
            'full_name': full_name,
            'role': 'user', 
            'status': 'active',
            'creation_date': datetime.utcnow(),
            'subscribed_services': subscribed_services
        }
        db.collection('users').document(new_user_auth.uid).set(user_data)
        
    except Exception as e:
        print(f"Error creating user: {e}")

    return redirect(url_for('views.admin_home', lang_code=lang_code))
