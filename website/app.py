import boto3
import os
import requests
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

API_GATEWAY_URL = "https://mr32irnm08.execute-api.eu-central-1.amazonaws.com/prod/send-message"
lambda_client = boto3.client('lambda')
s3 = boto3.client('s3')
BUCKET_NAME = 'sharon088-lambdas-bucket'
CSV_PREFIX = 'csv/'
CONVERTED_PREFIX = 'converted/'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-message', methods=['POST'])
def send_message():
    """ Find chat ID at: https://api.telegram.org/bot7679655459:AAEfC32TSr-NceQf8XtMKNYThTw2-GFm0GY/getUpdates"""
    contacts = request.form.getlist('contacts')
    message = request.form['message']
    if not contacts or not message:
        return jsonify({"error": "Contacts or message not provided"}), 400
    payload = {
        'contacts': contacts,
        'message': message
    }
    try:
        response = requests.post(API_GATEWAY_URL, json=payload)
        response_data = response.json()
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "Messages sent successfully!"}), 200
        else:
            return jsonify({"status": "error", "message": response_data.get("message", "Error sending messages.")}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to connect to API: {str(e)}"}), 500
    
@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    """ Upload CSV file to S3 bucket, to be converted into Excel file """
    if 'csv-file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400
    file = request.files['csv-file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400
    try:
        file_key = f"{CSV_PREFIX}{file.filename}"
        s3.upload_fileobj(file, BUCKET_NAME, file_key)
        converted_key = f"converted/{os.path.splitext(file.filename)[0]}.xlsx"
        download_url = f"https://{BUCKET_NAME}.s3.eu-central-1.amazonaws.com/{converted_key}"
        return jsonify({
            "status": "success",
            "message": "File uploaded successfully and will be converted shortly.",
            "download_url": download_url
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/wikipedia', methods=['POST'])
def fetch_wikipedia_summary():
    """ Get Wikipedia's topic from user to fetch its summary section"""
    data = request.get_json()
    topic = data.get('topic')   
    if not topic:
        return jsonify({"status": "error", "message": "Topic is required"}), 400
    lambda_payload = {"topic": topic}  
    try:
        response = lambda_client.invoke(
            FunctionName="get_info",
            InvocationType="RequestResponse",
            Payload=json.dumps(lambda_payload)
        )
        response_payload = json.loads(response['Payload'].read().decode('utf-8'))
        if response['StatusCode'] == 200:
            return jsonify({
                "status": "success",
                "message": response_payload.get('body', 'Wikipedia summary fetched successfully!'),
                "download_url": f"https://{BUCKET_NAME}.s3.eu-central-1.amazonaws.com/wikipedia.txt"
            })
        else:
            return jsonify({
                "status": "error",
                "message": response_payload.get("message", "Failed to fetch summary")
            }), 500
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to invoke Lambda: {str(e)}"}), 500
    
@app.route('/upload-backup', methods=['POST'])
def upload_backup():
    """ Upload file to S3 bucket, to be backed up with Lambda and Cron """
    if 'backup-file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400
    file = request.files['backup-file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400
    try:
        file_key = f"files_to_backup/{file.filename}"
        s3.upload_fileobj(file, BUCKET_NAME, file_key)
        file_url = f"https://{BUCKET_NAME}.s3.eu-central-1.amazonaws.com/{file_key}"
        return jsonify({
            "status": "success",
            "message": "File uploaded successfully!",
            "file_url": file_url
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/create-project', methods=['POST'])
def create_gitlab_project():
    """ Create a new GitLab project using Lambda function """
    try:
        data = request.get_json()
        project_name = data.get('project_name')
        if not project_name:
            return jsonify({"status": "error", "message": "Project name is required"}), 400
        lambda_payload = {"project_name": project_name}
        response = lambda_client.invoke(
            FunctionName="new_project",
            InvocationType="RequestResponse",
            Payload=json.dumps(lambda_payload)
        )
        response_payload = json.loads(response['Payload'].read().decode('utf-8'))
        if response['StatusCode'] == 200:
            return jsonify({
                "status": "success",
                "message": response_payload.get('message', 'Project created successfully!'),
                "details": response_payload.get('details', {})
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": response_payload.get('message', 'Failed to create project.')
            }), 500
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to invoke Lambda: {str(e)}"}), 500

@app.route('/create-user', methods=['POST'])
def create_gitlab_user():
    """ Create a new user in GitLab with a specific role and repository """
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        if not all([name, email, username, password]):
            return jsonify({"status": "error", "message": "All fields are required"}), 400
        lambda_payload = {
            "name": name,
            "email": email,
            "username": username,
            "password": password
        }
        response = lambda_client.invoke(
            FunctionName="create_user",
            InvocationType="RequestResponse",
            Payload=json.dumps(lambda_payload)
        )
        response_payload = json.loads(response['Payload'].read().decode('utf-8'))
        if response['StatusCode'] == 200:
            return jsonify({
                "status": "success",
                "message": response_payload.get('message', 'User created successfully!'),
                "details": response_payload
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": response_payload.get('message', 'Failed to create user.')
            }), 500
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to invoke Lambda: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)