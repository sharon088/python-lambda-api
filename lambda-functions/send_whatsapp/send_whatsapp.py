import os
import requests
import json

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

def send_telegram_message(chat_id, message):
    """ Sends a Telegram message to a specific chat ID """
    payload = {
        "chat_id": chat_id,
        "text": message,
    }
    response = requests.post(TELEGRAM_API_URL, json=payload)
    return response.json()

def lambda_handler(event, context):
    """
    Lambda handler to send Telegram messages to multiple contacts.
    Expects `contacts` and `message` from the HTML form via API Gateway.
    """
    try:
        body = json.loads(event.get("body", "{}"))
        contacts = body.get("contacts", [])
        message = body.get("message", "")
        
        if not contacts or not message:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Contacts and message are required."})
            }
        
        results = []
        for contact in contacts:
            result = send_telegram_message(contact, message)
            results.append({"contact": contact, "result": result})
        
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Messages sent.", "details": results})
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }