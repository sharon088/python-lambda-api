import gitlab
import os
import requests

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

GITLAB_URL = os.environ.get('GITLAB_URL', '')
PRIVATE_TOKEN = os.environ.get('GITLAB_TOKEN', '')
MAIN_GROUP_ID = 2

def send_telegram_message(chat_id, message):
    """ Sends a Telegram message to a specific chat ID """
    payload = {
        "chat_id": chat_id,
        "text": message,
    }
    response = requests.post(TELEGRAM_API_URL, json=payload)
    return response.json()

def send_operation_notification(message):
    """Send success/failure notification to a Telegram chat"""
    admin_chat_id = os.environ['ADMIN_CHAT_ID']
    send_telegram_message(admin_chat_id, message)

def lambda_handler(event, context):
    try:
        name = event.get('name')
        email = event.get('email')
        username = event.get('username')
        password = event.get('password')

        if not all([name, email, username, password]):
            error_message = "All fields are required."
            send_operation_notification(f"Failure: {error_message}")
            return {"statusCode": 400, "message": error_message}

        gl = gitlab.Gitlab(GITLAB_URL, private_token=PRIVATE_TOKEN)

        user_data = {
            'name': name,
            'username': username,
            'email': email,
            'password': password,
            'reset_password': False
        }
        user = gl.users.create(user_data)

        group = gl.groups.get(MAIN_GROUP_ID)
        group.members.create({'user_id': user.id, 'access_level': gitlab.REPORTER})

        project = gl.projects.create({
            'name': name,
            'namespace_id': group.id
        })

        success_message = f"User and project created successfully!\nUser ID: {user.id}\nProject ID: {project.id}\nProject URL: {project.web_url}"
        send_operation_notification(f"Success: {success_message}")

        return {
            "statusCode": 200,
            "message": "User and repository created successfully!",
            "details": {
                "user_id": user.id,
                "user_email": user.email,
                "project_id": project.id,
                "project_url": project.web_url
            }
        }

    except gitlab.exceptions.GitlabCreateError as e:
        error_message = f"GitLab API error: {e.error_message}"
        send_operation_notification(f"Failure: {error_message}")
        return {"statusCode": 400, "message": error_message}

    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        send_operation_notification(f"Failure: {error_message}")
        return {"statusCode": 500, "message": error_message}