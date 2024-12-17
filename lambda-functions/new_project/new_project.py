import gitlab
import os
import requests

GITLAB_URL = "https://gitlab.com"
PRIVATE_TOKEN = os.environ['GITLAB_TOKEN']
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
        project_name = event.get('project_name')
        if not project_name:
            error_message = "Project name is required."
            send_telegram_message(f"❌ Error: {error_message}")
            return {"statusCode": 400, "message": error_message}
        
        gl = gitlab.Gitlab(GITLAB_URL, private_token=PRIVATE_TOKEN)
        project = gl.projects.create({'name': project_name})
        
        readme_content = f"# {project_name}\n\nHello, World!"
        project.files.create({
            'file_path': 'README.md',
            'branch': 'main',
            'content': readme_content,
            'commit_message': 'Initial commit: Add README.md'
        })
        
        success_message = (
            f"✅ Project '{project_name}' created successfully!\n"
            f"📄 Project ID: {project.id}\n"
            f"🌐 URL: {project.web_url}"
        )
        send_telegram_message(success_message)
        
        return {
            "statusCode": 200,
            "message": success_message,
            "details": {
                "project_id": project.id,
                "project_url": project.web_url
            }
        }
    
    except gitlab.exceptions.GitlabCreateError as e:
        error_message = f"GitLab API error: {e.error_message}"
        send_telegram_message(f"❌ Error: {error_message}")
        return {"statusCode": 400, "message": error_message}
    
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        send_telegram_message(f"❌ Error: {error_message}")
        return {"statusCode": 500, "message": error_message}