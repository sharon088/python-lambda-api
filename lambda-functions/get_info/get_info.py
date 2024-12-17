import json
import os
import boto3
import requests

s3 = boto3.client('s3')
BUCKET_NAME = 'tasty-kfc-bucket'
WIKIPEDIA_FILE_KEY = 'wikipedia.txt'

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

""" test devops goofy niv, devops goofy """

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
    topic = event.get('topic')
    if not topic:
        error_message = "Topic is required"
        send_telegram_message(error_message)
        return {
            'statusCode': 400,
            'body': json.dumps({'message': error_message})
        }

    url = f'https://en.wikipedia.org/api/rest_v1/page/summary/{topic}'
    try:
        response = requests.get(url)
        if response.status_code != 200:
            error_message = f"Failed to fetch Wikipedia summary for {topic}."
            send_telegram_message(error_message)
            return {
                'statusCode': 500,
                'body': json.dumps({'message': error_message})
            }

        data = response.json()
        summary = data.get('extract', 'No summary available.')

        try:
            s3_response = s3.get_object(Bucket=BUCKET_NAME, Key=WIKIPEDIA_FILE_KEY)
            existing_content = s3_response['Body'].read().decode('utf-8')
        except s3.exceptions.NoSuchKey:
            existing_content = ''

        updated_content = existing_content + f'\n\n{topic}:\n{summary}'

        s3.put_object(Bucket=BUCKET_NAME, Key=WIKIPEDIA_FILE_KEY, Body=updated_content)

        success_message = f"File uploaded to S3 at 's3://{BUCKET_NAME}/{WIKIPEDIA_FILE_KEY}'."
        send_telegram_message(success_message)

        return {
            "statusCode": 200,
            "body": success_message
        }

    except Exception as e:
        error_message = f"Error: {str(e)}"
        send_telegram_message(error_message)
        return {
            'statusCode': 500,
            'body': json.dumps({'message': error_message})
        }
