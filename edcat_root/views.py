
import os
import json
from flask import Blueprint, render_template, current_app, request, jsonify, redirect, url_for, g
from firebase_admin import auth
import functools
from datetime import datetime

# Import shared objects from the application factory
from edcat_root import db, get_secret

views = Blueprint('views', __name__)


def login_required(view):
    """Stateless decorator: verifies the '__session' cookie token on every request."""
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
            current_user_role = 'admin' if email in admin_emails else 'user'

            g.user_profile = {
                'uid': uid,
                'email': email,
                'full_name': g.user.get('name', ''),
                'role': current_user_role,
                'status': 'active'
            }

        except auth.InvalidIdTokenError:
            response = redirect(url_for('views.login', lang_code=lang_code))
            response.set_cookie('__session', '', expires=0)
            return response
        except Exception as e:
            print(f"Error in login_required decorator: {e}")
            response = redirect(url_for('views.login', lang_code=lang_code))
            response.set_cookie('__session', '', expires=0)
            return response

        return view(**kwargs)
    return wrapped_view


def admin_required(view):
    """Decorator that checks for 'admin' role. Must run AFTER login_required."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        user_profile = getattr(g, 'user_profile', {})
        if user_profile.get('role') != 'admin':
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
    """Receives ID token and sets it as the __session cookie."""
    try:
        id_token = request.json['token']
        response = jsonify({"status": "success"})
        is_prod = os.environ.get('GAE_ENV', '').startswith('standard')
        response.set_cookie('__session', id_token, httponly=True, secure=is_prod, samesite='Lax')
        return response

    except Exception as e:
        print(f"Error during session login: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@views.route("/logout")
def logout(lang_code):
    response = redirect(url_for('views.home', lang_code=lang_code))
    response.set_cookie('__session', '', expires=0)
    return response

# --- Admin Dashboard & User Management ---

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
    return render_template("admin_home.html", users=users_list)

@views.route("/create_user", methods=['POST'])
@login_required
@admin_required
def create_user(lang_code):
    if not db: return redirect(url_for('views.admin_home', lang_code=lang_code))
    try:
        full_name = request.form['fullName']
        email = request.form['email']
        password = request.form['password']
        status = request.form.get('status', 'active')

        new_user_auth = auth.create_user(email=email, password=password, display_name=full_name)
        
        admin_emails_str = get_secret('ADMIN_USERS')
        admin_emails = [e.strip() for e in admin_emails_str.split(',')] if admin_emails_str else []
        new_user_role = 'admin' if email in admin_emails else 'user'

        user_data = {
            'uid': new_user_auth.uid,
            'email': email,
            'full_name': full_name,
            'role': new_user_role,
            'status': status,
            'creation_date': datetime.utcnow(),
        }
        db.collection('users').document(new_user_auth.uid).set(user_data)
    except Exception as e:
        print(f"Error creating user: {e}")
    return redirect(url_for('views.admin_home', lang_code=lang_code))

@views.route("/admin/update_user_fields/<uid>", methods=['POST'])
@login_required
@admin_required
def update_user_fields(lang_code, uid):
    if not db: return jsonify({"status": "error", "message": "Database not connected"}), 500
    try:
        data_to_update = {}
        if 'status' in request.form:
            data_to_update['status'] = request.form['status']
        
        if data_to_update:
            db.collection('users').document(uid).update(data_to_update)
        return redirect(url_for('views.admin_home', lang_code=lang_code))
    except Exception as e:
        print(f"Error updating user fields: {e}")
        return redirect(url_for('views.admin_home', lang_code=lang_code))

@views.route("/admin/update_user/<uid>", methods=['POST'])
@login_required
@admin_required
def update_user(lang_code, uid):
    if not db: return jsonify({"status": "error", "message": "Database not connected"}), 500
    try:
        full_name = request.form.get('fullName')
        data_to_update = {'full_name': full_name}
        db.collection('users').document(uid).update(data_to_update)
        return redirect(url_for('views.admin_home', lang_code=lang_code))
    except Exception as e:
        print(f"Error updating user profile: {e}")
        return redirect(url_for('views.admin_home', lang_code=lang_code))
