import boto3
from datetime import datetime
import os
import requests

s3 = boto3.client('s3')

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

SOURCE_PREFIX = "files_to_backup/"
BACKUP_PREFIX = "backups/"
DATE_FORMAT = "%d-%m-%Y"

def send_telegram_message(message):
    """ Send a notification to Telegram """
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Telegram notification: {e}")

def list_files_in_prefix(bucket_name, prefix):
    """ List all files in the given bucket and prefix """
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    files = response.get("Contents", [])
    return [file["Key"] for file in files if file["Key"] != prefix]

def backup_files(bucket_name):
    """ Back up files from SOURCE_PREFIX to BACKUP_PREFIX """
    today = datetime.now()
    backup_folder = f"{BACKUP_PREFIX}{today.strftime(DATE_FORMAT)}/"
    files_to_backup = list_files_in_prefix(bucket_name, SOURCE_PREFIX)
    if not files_to_backup:
        error_message = f"No files found in prefix '{SOURCE_PREFIX}' to back up."
        send_telegram_message(error_message)
        print(error_message)
        return
    for file_key in files_to_backup:
        file_name = file_key[len(SOURCE_PREFIX):]
        backup_key = f"{backup_folder}{file_name}"
        s3.copy_object(
            Bucket=bucket_name,
            CopySource={'Bucket': bucket_name, 'Key': file_key},
            Key=backup_key
        )
        print(f"Backed up '{file_key}' to '{backup_key}'")

    success_message = f"Backup completed for {len(files_to_backup)} files."
    send_telegram_message(success_message)
    print(success_message)

def lambda_handler(event, context):
    bucket_name = "tasty-kfc-bucket"
    try:
        backup_files(bucket_name)
    except Exception as e:
        error_message = f"❌ Error: {str(e)}"
        send_telegram_message(error_message)
        print(error_message)
        raise
