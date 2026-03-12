
from flask import Blueprint, request, jsonify, current_app
import os

from ..views import login_required, load_user_profile, tester_or_admin_required

# --- MONOLITHIC ARCHITECTURE ---
# The RAG agent is now initialized and attached to the Flask app 
# during startup (in the app factory).
# This blueprint accesses the agent via `current_app`.

api_bp = Blueprint("api_bp", __name__)

@api_bp.route("/chat", methods=["POST"])
@login_required
@load_user_profile
@tester_or_admin_required
def chat():
    """Receives a user message, passes it to the integrated RagAgent, and returns the response."""
    
    data = request.get_json()
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "Nenhuma mensagem recebida."}), 400

    try:
        # Access the pre-initialized agent from the application context.
        # If the agent failed to initialize, the app wouldn't have started, so this call is safe.
        rag_agent = current_app.rag_agent
        
        # Invoke the agent directly.
        # The agent's `invoke` method handles the logic internally.
        assistant_response = rag_agent.invoke({"messages": [("user", user_message)]})

        return jsonify({"response": assistant_response})

    except Exception as e:
        # Catch any unexpected errors during agent invocation.
        error_message = f"Ocorreu um erro ao processar sua mensagem: {e}"
        print(error_message) # Log to server console
        # Using a 500 Internal Server Error is appropriate here.
        return jsonify({"error": error_message}), 500
