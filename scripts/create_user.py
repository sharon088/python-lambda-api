import gitlab
import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

load_dotenv()

GITLAB_URL = "http://localhost:9090/api/v4"
GROUP_ID = os.getenv("GROUP_ID")
GITLAB_TOKEN = os.getenv("GITLAB_SERVER_TOKEN")
GOOGLE_SHEET_NAME = "Python script GitLab"
CREDNTIALS = "credentials.json"

def initialize_gitlab():
    return gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_TOKEN)

def setup_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDNTIALS, scope)
    client = gspread.authorize(creds)
    return client

def parse_google_sheet():
    client = setup_google_sheets()
    sheet = client.open(GOOGLE_SHEET_NAME).sheet1
    employees = sheet.get_all_records()
    return employees

def create_gitlab_user(gl, employee):
    try:
        user = gl.users.create({
            'email': employee['Email'],
            'password': employee['Password'],  
            'username': employee['Username'],
            'name': employee['Name'],
        })
        print(f"User {employee['Username']} created successfully.")
        return user
    except gitlab.exceptions.GitlabCreateError as e:
        print(f"Failed to create user {employee['Username']}: {e}")
        return None

def add_user_to_group(gl, user):
    try:
        group = gl.groups.get(GROUP_ID)
        group.members.create({'user_id': user.id, 'access_level': gitlab.const.AccessLevel.REPORTER})
        print(f"User {user.username} added to group with Reporter role.")
    except gitlab.exceptions.GitlabCreateError as e:
        print(f"Failed to add user {user.username} to the group: {e}")

def create_user_repository(gl, user):
    try:
        group = gl.groups.get(GROUP_ID) 
        project = gl.projects.create({
            'name': user.username,
            'namespace_id': group.id,
        })
        print(f"Repository {project.name} created successfully in group {group.name}.")
    except gitlab.exceptions.GitlabCreateError as e:
        print(f"Failed to create repository for {user.username}: {e}")

def main():
    gl_client = initialize_gitlab()
    employees = parse_google_sheet()
    for employee in employees:
        user = create_gitlab_user(gl_client, employee)
        if user:
            add_user_to_group(gl_client, user)
            create_user_repository(gl_client, user)

if __name__ == "__main__":
    main()