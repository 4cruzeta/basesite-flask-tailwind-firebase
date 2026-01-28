
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

            # Fetch user profile from Firestore
            user_profile_data = {}
            if db:
                user_ref = db.collection('users').document(uid)
                user_doc = user_ref.get()
                if user_doc.exists:
                    user_profile_data = user_doc.to_dict()

            g.user_profile = {
                'uid': uid,
                'email': email,
                'full_name': user_profile_data.get('full_name', g.user.get('name', '')),
                'role': user_profile_data.get('role', current_user_role),
                'status': user_profile_data.get('status', 'active')
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
            return redirect(url_for('views.user_home', lang_code=lang_code))
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
        response.set_cookie(
            '__session', 
            id_token, 
            httponly=True, 
            secure=True, 
            samesite='None'
        )
        return response

    except Exception as e:
        print(f"Error during session login: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@views.route("/logout")
def logout(lang_code):
    response = redirect(url_for('views.home', lang_code=lang_code))
    response.set_cookie('__session', '', expires=0)
    return response

# --- Role-Based Dashboards ---

@views.route("/dashboard")
@login_required
def dashboard(lang_code):
    """Redirects user to the appropriate dashboard based on their role."""
    user_profile = getattr(g, 'user_profile', {})
    if user_profile.get('role') == 'admin':
        return redirect(url_for('views.admin_home', lang_code=lang_code))
    else:
        return redirect(url_for('views.user_home', lang_code=lang_code))

@views.route("/user_home")
@login_required
def user_home(lang_code):
    return render_template("user_home.html")

@views.route("/user_profile")
@login_required
def user_profile(lang_code):
    return render_template("user_profile.html")

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

@views.route("/api/user/<uid>", methods=['GET'])
@login_required
@admin_required
def get_user_data(lang_code, uid):
    """API endpoint to fetch data for a single user."""
    if not db:
        return jsonify({"status": "error", "message": "Database not connected"}), 500
    try:
        user_ref = db.collection('users').document(uid)
        user_doc = user_ref.get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            if 'creation_date' in user_data and hasattr(user_data['creation_date'], 'isoformat'):
                user_data['creation_date'] = user_data['creation_date'].isoformat()
            return jsonify(user_data)
        else:
            return jsonify({"status": "error", "message": "User not found"}), 404
    except Exception as e:
        print(f"Error fetching user data for {uid}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

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
