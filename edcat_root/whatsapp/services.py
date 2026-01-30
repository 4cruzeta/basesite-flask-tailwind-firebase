
import os
import requests
from google.cloud import secretmanager

# It's good practice to instantiate the client once per process.
client = secretmanager.SecretManagerServiceClient()

# A simple in-memory cache to avoid fetching the same secret multiple times
# within the same application instance lifecycle.
_secret_cache = {}

def _access_secret_version(secret_id: str) -> str | None:
    """
    Access the latest version of a secret from Google Secret Manager.
    Includes in-memory caching to reduce API calls.
    """
    if secret_id in _secret_cache:
        return _secret_cache[secret_id]

    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        print("CRITICAL: GOOGLE_CLOUD_PROJECT environment variable not set.")
        return None

    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"

    try:
        # Access the secret version.
        response = client.access_secret_version(request={"name": name})
        secret = response.payload.data.decode("UTF-8")
        _secret_cache[secret_id] = secret
        return secret
    except Exception as e:
        # In a production environment, you would have more robust logging (e.g., Google Cloud Logging).
        print(f"ERROR: Could not access secret '{secret_id}'. Reason: {e}")
        return None

def get_whatsapp_credentials() -> dict:
    """
    Retrieves all necessary WhatsApp credentials from Google Secret Manager.

    Returns:
        A dictionary containing the access_token, phone_number_id, and verify_token.

    Raises:
        RuntimeError: If any of the required credentials cannot be fetched.
    """
    access_token = _access_secret_version("WHATSAPP_ACCESS_TOKEN")
    phone_number_id = _access_secret_version("WHATSAPP_PHONE_NUMBER_ID")
    verify_token = _access_secret_version("WHATSAPP_VERIFY_TOKEN")

    if not all([access_token, phone_number_id, verify_token]):
        raise RuntimeError(
            "FATAL: One or more WhatsApp credentials could not be retrieved "
            "from Secret Manager. Ensure they are set and the service account "
            "has the 'Secret Manager Secret Accessor' role."
        )

    return {
        "access_token": access_token,
        "phone_number_id": phone_number_id,
        "verify_token": verify_token,
    }

def send_whatsapp_message(to: str, message_text: str) -> requests.Response:
    """
    Sends a WhatsApp message using the Meta Graph API.

    Args:
        to: The recipient's phone number in international format.
        message_text: The text of the message to send.

    Returns:
        The response object from the requests library.
    """
    credentials = get_whatsapp_credentials()
    api_version = "v19.0"  # It's good practice to lock the API version
    url = f"https://graph.facebook.com/{api_version}/{credentials['phone_number_id']}/messages"
    
    headers = {
        "Authorization": f"Bearer {credentials['access_token']}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message_text},
    }

    print(f"Attempting to send message to {to}...")
    response = requests.post(url, json=payload, headers=headers)
    
    # Log response for debugging purposes
    print(f"Meta API Response Status: {response.status_code}")
    print(f"Meta API Response Body: {response.json()}")
    
    response.raise_for_status()  # Raise an exception for HTTP error codes
    
    return response

