from dotenv import load_dotenv
import os
import requests
from typing import Dict, Any, List

load_dotenv()

GRAPH_API_TOKEN = os.getenv("GRAPH_API_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
WHATSAPP_API_URL = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"


def send_text_message(phone_number: str, message: str) -> Dict[str, Any]:
    """
    Send a text message to WhatsApp user
    """
    try:
        headers = {
            "Authorization": f"Bearer {GRAPH_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }
        
        response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        print(f"Text message sent to {phone_number}: {message[:50]}...")
        return {"success": True, "response": response.json()}
        
    except Exception as e:
        print(f"Error sending text message: {e}")
        return {"success": False, "error": str(e)}
