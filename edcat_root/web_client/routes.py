from flask import Blueprint, render_template
from ..views import login_required, load_user_profile, admin_required

# Define a new Blueprint for the web client. 
# The templates are expected to be in a 'templates' folder in the same directory.
web_client_bp = Blueprint(
    'web_client_bp',
    __name__,
    template_folder='templates'
)

@web_client_bp.route("/chat")
@login_required
@load_user_profile
@admin_required
def chat(lang_code):
    """Renders the main chat interface for admins."""
    # Renders the 'chat.html' file from the 'templates' folder in this directory.
    return render_template("chat.html")
