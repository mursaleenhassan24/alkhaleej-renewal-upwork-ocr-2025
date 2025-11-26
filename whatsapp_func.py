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


def format_extraction_message(
    request_id: str,
    client_name: str,
    qatar_id_data: Dict[str, Any],
    istimara_data: Dict[str, Any]
) -> str:
    """
    Format extracted data into a readable WhatsApp message
    """
    message = f"*Document Processing Complete*\n\n"
    message += f"*Request ID:* {request_id}\n"
    message += f"*Client Name:* {client_name}\n"
    message += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Qatar ID Information
    message += "*QATAR ID INFORMATION*\n\n"
    
    if qatar_id_data.get("name"):
        message += f"*Name:* {qatar_id_data['name']}\n"
    
    if qatar_id_data.get("id_no"):
        message += f"*Qatar ID:* {qatar_id_data['id_no']}\n"
    
    if qatar_id_data.get("dob"):
        message += f"*Date of Birth:* {qatar_id_data['dob']}\n"
    
    if qatar_id_data.get("nationality"):
        message += f"*Nationality:* {qatar_id_data['nationality']}\n"
    
    if qatar_id_data.get("occupation"):
        message += f"*Occupation:* {qatar_id_data['occupation']}\n"
    
    if qatar_id_data.get("employer"):
        message += f"*Employer:* {qatar_id_data['employer']}\n"
    
    if qatar_id_data.get("expiry_date"):
        message += f"*Expiry Date:* {qatar_id_data['expiry_date']}\n"
    
    if qatar_id_data.get("passport_number"):
        message += f"*Passport No:* {qatar_id_data['passport_number']}\n"
    
    if qatar_id_data.get("passport_expiry"):
        message += f"*Passport Expiry:* {qatar_id_data['passport_expiry']}\n"
    
    # Istimara Information
    message += "\n━━━━━━━━━━━━━━━━━━━━\n"
    message += "*ISTIMARA (VEHICLE) INFORMATION*\n\n"
    
    if istimara_data.get("owner_en"):
        message += f"*Owner:* {istimara_data['owner_en']}\n"
    
    if istimara_data.get("owner_qid"):
        message += f"*Owner QID:* {istimara_data['owner_qid']}\n"
    
    if istimara_data.get("vehicle_number"):
        message += f"*Vehicle Number:* {istimara_data['vehicle_number']}\n"
    
    if istimara_data.get("vehicle_make"):
        message += f"*Make:* {istimara_data['vehicle_make']}\n"
    
    if istimara_data.get("vehicle_model"):
        message += f"*Model:* {istimara_data['vehicle_model']}\n"
    
    if istimara_data.get("vehicle_year"):
        message += f"*Year:* {istimara_data['vehicle_year']}\n"
    
    if istimara_data.get("vehicle_color"):
        message += f"*Color:* {istimara_data['vehicle_color']}\n"
    
    if istimara_data.get("vehicle_type"):
        message += f"*Type:* {istimara_data['vehicle_type']}\n"
    
    if istimara_data.get("vehicle_chassis_no"):
        message += f"*Chassis No:* {istimara_data['vehicle_chassis_no']}\n"
    
    if istimara_data.get("vehicle_engine_no"):
        message += f"*Engine No:* {istimara_data['vehicle_engine_no']}\n"
    
    if istimara_data.get("vehicle_expiry_date"):
        message += f"*Registration Expiry:* {istimara_data['vehicle_expiry_date']}\n"
    
    if istimara_data.get("vehicle_insurance_company"):
        message += f"\n*Insurance Company:* {istimara_data['vehicle_insurance_company']}\n"
    
    if istimara_data.get("vehicle_policy_number"):
        message += f"*Policy Number:* {istimara_data['vehicle_policy_number']}\n"
    
    if istimara_data.get("vehicle_expiry"):
        message += f"*Vehicle Expiry:* {istimara_data['vehicle_expiry']}\n"
    
    return message