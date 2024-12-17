import boto3
import os
import csv
from xlsxwriter.workbook import Workbook
import requests

s3 = boto3.client('s3')

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

def send_telegram_message(message):
    """ Send a notification to Telegram """
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Telegram notification: {e}")

def lambda_handler(event, context):
    try:
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        object_key = event['Records'][0]['s3']['object']['key']
        
        download_path = f"/tmp/{os.path.basename(object_key)}"
        upload_path = f"/tmp/{os.path.splitext(os.path.basename(object_key))[0]}.xlsx"

        s3.download_file(bucket_name, object_key, download_path)

        workbook = Workbook(upload_path)
        worksheet = workbook.add_worksheet()

        with open(download_path, 'rt', encoding='utf8') as f:
            reader = csv.reader(f)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    worksheet.write(r, c, col)
        workbook.close()

        converted_key = f"converted/{os.path.splitext(os.path.basename(object_key))[0]}.xlsx"
        s3.upload_file(upload_path, bucket_name, converted_key)

        success_message = (
            f"✅ File conversion successful!\n"
            f"📄 Source File: {object_key}\n"
            f"📥 Converted File: {converted_key}"
        )
        send_telegram_message(success_message)
        
        return {
            "statusCode": 200,
            "body": f"Successfully converted {object_key} to {converted_key}"
        }
    
    except Exception as e:
        error_message = f"❌ Error: {str(e)}"
        send_telegram_message(error_message)   
        return {
            "statusCode": 500,
            "body": error_message
        }