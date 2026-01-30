
from flask import Blueprint, request, current_app
from .services import get_whatsapp_credentials, send_whatsapp_message
import logging

# It's good practice to use a logger for better debugging and monitoring.
logging.basicConfig(level=logging.INFO)

# Define the Blueprint for WhatsApp routes
whatsapp_bp = Blueprint(
    "whatsapp_bp", __name__, template_folder="templates", static_folder="static"
)

@whatsapp_bp.route("/webhooks/whatsapp", methods=["GET", "POST"])
def handle_webhook():
    """
    Handles both verification (GET) and incoming message notifications (POST)
    from the Meta WhatsApp Business API.
    """
    try:
        credentials = get_whatsapp_credentials()
        verify_token = credentials.get("verify_token")

        if request.method == "GET":
            # This is the verification request from Meta.
            mode = request.args.get("hub.mode")
            token = request.args.get("hub.verify_token")
            challenge = request.args.get("hub.challenge")

            if mode == "subscribe" and token == verify_token:
                logging.info("WEBHOOK_VERIFIED")
                return challenge, 200
            else:
                logging.warning("Webhook verification failed. Tokens do not match.")
                return "Forbidden", 403

        elif request.method == "POST":
            # This is an incoming message notification.
            data = request.get_json()
            logging.info(f"Received POST request with data: {data}")

            # Extract message details safely
            try:
                # The payload structure can be complex, so we navigate it carefully.
                change = data["entry"][0]["changes"][0]
                if change["field"] == "messages":
                    message_data = change["value"]["messages"][0]
                    sender_phone = message_data["from"]
                    message_body = message_data["text"]["body"]
                    
                    # --- ECHO LOGIC ---
                    # Send the received message back to the user.
                    logging.info(f"Sending echo message to {sender_phone}")
                    response_text = f"Eco: {message_body}"
                    send_whatsapp_message(to=sender_phone, message_text=response_text)
                    
            except (KeyError, IndexError) as e:
                # This handles cases where the payload is not a user message (e.g., status updates)
                logging.warning(f"Could not parse message from payload. Payload might not be a user message. Error: {e}")

            # You must respond with a 200 OK to Meta within seconds.
            return "", 204

    except Exception as e:
        # A general catch-all for unexpected errors.
        logging.error(f"An unexpected error occurred in webhook handler: {e}", exc_info=True)
        return "Internal Server Error", 500
