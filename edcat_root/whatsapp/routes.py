
import logging
from flask import Blueprint, request, current_app

from .services import get_whatsapp_credentials, send_whatsapp_message

logging.basicConfig(level=logging.INFO)

whatsapp_bp = Blueprint(
    "whatsapp_bp", __name__, template_folder="templates", static_folder="static"
)

@whatsapp_bp.route("/webhooks/whatsapp", methods=["GET", "POST", "PUT"])
def handle_webhook():
    """Handles webhook verification and incoming user messages."""
    # 1. Handle webhook verification
    if request.method == "GET":
        credentials = get_whatsapp_credentials()
        verify_token = credentials.get("verify_token")
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == verify_token:
            logging.info("SUCCESS: Webhook verified.")
            return challenge, 200
        else:
            logging.warning("Webhook verification failed.")
            return "Forbidden", 403

    # 2. Handle incoming events
    elif request.method == "POST" or request.method == "PUT":
        try:
            data = request.get_json()
            if not data or not data.get("entry"):
                return "OK", 200

            value = data["entry"][0]["changes"][0].get("value", {})

            if value.get("messages"):
                message_data = value["messages"][0]
                sender_phone = message_data.get("from")
                message_body = message_data.get("text", {}).get("body", "")
                message_id = message_data.get("id")
                
                if not message_body:
                    return "OK", 200

                logging.info(f'Received message from {sender_phone} (ID: {message_id}): "{message_body}" ')

                # --- CORRECTED: Access agent via app context and use invoke ---
                logging.info("Sending query to RAG Agent...")
                agent = current_app.rag_agent
                agent_response = agent.invoke({"messages": [("user", message_body)]})

                logging.info(f"Sending agent response to {sender_phone}: \"{agent_response}\"")
                send_whatsapp_message(to=sender_phone, message_text=agent_response)

            elif value.get("message_echoes"):
                echo_data = value["message_echoes"][0]
                logging.info(f"Received a message echo for message ID: {echo_data.get('id')}")

        except Exception as e:
            logging.error(f"Error processing webhook event: {e}", exc_info=True)

        return "OK", 200

    return "Not Found", 404
