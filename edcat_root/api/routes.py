from flask import Blueprint, request, jsonify
from ..views import login_required, load_user_profile, admin_required

api_bp = Blueprint("api_bp", __name__)

@api_bp.route("/chat", methods=["POST"])
@login_required
@load_user_profile
@admin_required
def chat():
    """Receives user message and returns the assistant's response."""
    # Late import of the AGENT INSTANCE to prevent circular dependencies.
    from ..rag_agent.agent import rag_agent
    
    data = request.get_json()
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "Nenhuma mensagem recebida."}), 400

    try:
        # Call the generate_response METHOD on the agent instance.
        assistant_response = rag_agent.generate_response(user_message)
        return jsonify({"response": assistant_response})
    except Exception as e:
        # Basic error logging, can be improved
        print(f"Error calling RAG agent: {e}")
        return jsonify({"error": "Desculpe, não foi possível conectar ao assistente."}), 500
