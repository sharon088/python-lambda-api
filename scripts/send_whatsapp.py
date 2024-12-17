import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pywhatkit
import pyautogui
import time

def setup_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    return client

def read_contacts_from_sheet(sheet_name):
    client = setup_google_sheets()
    sheet = client.open(sheet_name).sheet1
    data = sheet.get_all_records()
    return data

def send_whatsapp_message(phone_number, message):
    try:
        phone_number = str(phone_number).strip()
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number     
        message = str(message)       
        print(f"Sending to {phone_number}: {message}")      
        pywhatkit.sendwhatmsg_instantly(phone_number, message)
        time.sleep(5)
        pyautogui.press("enter")
        print(f"Message sent to {phone_number}: {message}")        
        time.sleep(20)

    except Exception as e:
        print(f"Error sending message to {phone_number}: {e}")

def main():
    sheet_name = "Python script whatsapp"
    contacts = read_contacts_from_sheet(sheet_name)
    for contact in contacts:
        send_whatsapp_message(contact['Phone Number'], contact['Message'])

if __name__ == "__main__":
    main()