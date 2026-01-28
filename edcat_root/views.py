
import os
import json
from flask import Blueprint, render_template, current_app, request, jsonify, redirect, url_for, g
from firebase_admin import auth
from firebase_admin.exceptions import FirebaseError
import functools
from datetime import datetime

# Import shared objects from the application factory
from edcat_root import db, get_secret

views = Blueprint('views', __name__)

# --- Decorators for Authentication and User Profile Loading ---

def login_required(view):
    """Decorator to verify Firebase session cookie. Populates g.user with auth data."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        lang_code = kwargs.get('lang_code', 'pt_BR')
        id_token = request.cookies.get('__session')

        if not id_token:
            return redirect(url_for('views.login', lang_code=lang_code))

        try:
            g.user = auth.verify_id_token(id_token)
        except (auth.InvalidIdTokenError, auth.ExpiredIdTokenError) as e:
            # Clear the invalid cookie and redirect to login
            response = redirect(url_for('views.login', lang_code=lang_code))
            response.set_cookie('__session', '', expires=0)
            return response
        except Exception as e:
            # Handle other potential errors during token verification
            print(f"Unhandled error in login_required decorator: {e}")
            return "An unexpected error occurred", 500

        return view(**kwargs)
    return wrapped_view

def load_user_profile(view):
    """Decorator to load user profile from Firestore. Must run AFTER @login_required."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not hasattr(g, 'user'):
            # This should not happen if decorators are ordered correctly
            return "Authentication context not found", 500
        
        uid = g.user['uid']
        email = g.user.get('email')
        user_profile_data = {}
        
        # Determine default role based on ADMIN_USERS secret
        admin_emails_str = get_secret('ADMIN_USERS')
        admin_emails = [e.strip() for e in admin_emails_str.split(',')] if admin_emails_str else []
        default_role = 'admin' if email in admin_emails else 'user'

        # Fetch profile from Firestore, if the database is available
        if db:
            user_ref = db.collection('users').document(uid)
            user_doc = user_ref.get()
            if user_doc.exists:
                user_profile_data = user_doc.to_dict()

        # Populate g.user_profile with combined data, prioritizing Firestore data
        g.user_profile = {
            'uid': uid,
            'email': email,
            'full_name': user_profile_data.get('full_name', g.user.get('name', '')),
            'role': user_profile_data.get('role', default_role),
            'status': user_profile_data.get('status', 'active')
        }

        return view(**kwargs)
    return wrapped_view

def admin_required(view):
    """Decorator to ensure user has 'admin' role. Must run AFTER @load_user_profile."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not getattr(g, 'user_profile', {}).get('role') == 'admin':
            lang_code = kwargs.get('lang_code', 'pt_BR')
            # For API requests, return a JSON error instead of redirecting
            if request.path.startswith('/api/'):
                return jsonify({"success": False, "error": "Admin access required"}), 403
            # For web pages, redirect non-admins to their own user home page
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
    try:
        id_token = request.json['token']
        response = jsonify({"success": True})
        response.set_cookie(
            '__session', 
            id_token, 
            httponly=True, 
            secure=True, 
            samesite='None'
        )
        return response
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@views.route("/logout")
def logout(lang_code):
    response = redirect(url_for('views.home', lang_code=lang_code))
    response.set_cookie('__session', '', expires=0)
    return response

# --- Role-Based Dashboards ---

@views.route("/dashboard")
@login_required
@load_user_profile
def dashboard(lang_code):
    """Redirects user to the appropriate dashboard based on their role."""
    if g.user_profile.get('role') == 'admin':
        return redirect(url_for('views.admin_home', lang_code=lang_code))
    else:
        return redirect(url_for('views.user_home', lang_code=lang_code))

@views.route("/user_home")
@login_required
@load_user_profile
def user_home(lang_code):
    return render_template("user_home.html")

@views.route("/user_profile")
@login_required
@load_user_profile
def user_profile(lang_code):
    return render_template("user_profile.html")

# --- Admin Dashboard & User Management ---

@views.route("/admin_home")
@login_required
@load_user_profile
@admin_required
def admin_home(lang_code):
    users_list = []
    if not db:
        return render_template("admin_home.html", users=users_list, error="Database not connected")
    try:
        users_ref = db.collection('users').stream()
        for user in users_ref:
            user_data = user.to_dict()
            user_data['uid'] = user.id
            users_list.append(user_data)
    except FirebaseError as e:
        print(f"Error fetching users: {e}")
        return render_template("admin_home.html", users=[], error=f"Error fetching users: {e}")
    return render_template("admin_home.html", users=users_list)

@views.route("/api/user/<uid>", methods=['GET'])
@login_required
@load_user_profile # <-- FIX: Added the missing decorator
@admin_required
def get_user_data(lang_code, uid):
    if not db: return jsonify({"success": False, "error": "Database not connected"}), 500
    try:
        user_ref = db.collection('users').document(uid)
        user_doc = user_ref.get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            # Convert datetime to ISO format for JSON serialization
            if 'creation_date' in user_data and hasattr(user_data['creation_date'], 'isoformat'):
                user_data['creation_date'] = user_data['creation_date'].isoformat()
            return jsonify(user_data)
        else:
            return jsonify({"success": False, "error": "User not found"}), 404
    except FirebaseError as e:
        return jsonify({"success": False, "error": f"Firestore error: {e}"}), 500

@views.route("/create_user", methods=['POST'])
@login_required
@load_user_profile
@admin_required
def create_user(lang_code):
    if not db: return redirect(url_for('views.admin_home', lang_code=lang_code, error="db_error"))
    try:
        # Required fields
        email = request.form['email']
        password = request.form['password']
        
        # Optional fields
        full_name = request.form.get('fullName', '')
        status = request.form.get('status', 'active')
        
        new_user_auth = auth.create_user(email=email, password=password, display_name=full_name)
        
        admin_emails_str = get_secret('ADMIN_USERS')
        admin_emails = [e.strip() for e in admin_emails_str.split(',')] if admin_emails_str else []
        role = 'admin' if email in admin_emails else 'user'

        user_data = {
            'email': email,
            'full_name': full_name,
            'role': role,
            'status': status,
            'creation_date': datetime.utcnow(),
        }
        db.collection('users').document(new_user_auth.uid).set(user_data)

    except (KeyError, ValueError) as e:
        # Handle missing form fields
        print(f"Error creating user due to missing form field: {e}")
    except auth.EmailAlreadyExistsError as e:
        print(f"Error creating user: {e}")
    except FirebaseError as e:
        print(f"Firebase error creating user: {e}")

    return redirect(url_for('views.admin_home', lang_code=lang_code))

@views.route("/admin/update_user/<uid>", methods=['POST'])
@login_required
@load_user_profile
@admin_required
def update_user(lang_code, uid):
    """Unified route to update various user fields from the admin dashboard."""
    if not db: return jsonify({"success": False, "error": "Database not connected"}), 500
    
    try:
        data_to_update = {}
        allowed_fields = ['fullName', 'status', 'role'] # Add more editable fields here

        # Dynamically build the update dictionary from form data
        for field in allowed_fields:
            if field in request.form:
                data_to_update[field] = request.form[field]

        if data_to_update:
            # Special case for full name to also update Firebase Auth display name
            if 'fullName' in data_to_update:
                auth.update_user(uid, display_name=data_to_update['fullName'])
                # Rename to match Firestore field name
                data_to_update['full_name'] = data_to_update.pop('fullName')

            db.collection('users').document(uid).update(data_to_update)
        
        # Redirect back to admin home on success
        return redirect(url_for('views.admin_home', lang_code=lang_code))

    except FirebaseError as e:
        print(f"Error updating user {uid}: {e}")
        # On error, redirect with an error flash message (not implemented yet)
        return redirect(url_for('views.admin_home', lang_code=lang_code, error="update_failed"))
