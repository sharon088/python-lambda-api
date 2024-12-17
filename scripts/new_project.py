import os
import sys
import subprocess
import gitlab
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GITLAB_URL = "https://gitlab.com"
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
GITLAB_USERNAME = os.getenv("GITLAB_USERNAME")
GITLAB_LOCAL_DIR = os.path.expanduser("~/GitLab/")

if not GITLAB_TOKEN or not GITLAB_USERNAME:
    raise ValueError("GitLab token and username must be set in the .env file.")

def initialize_gitlab():
    """Initialize GitLab client."""
    return gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_TOKEN)

def create_gitlab_project(gl_client, project_name):
    """Create a new project in GitLab."""
    try:
        project = gl_client.projects.create({'name': project_name})
        print(f"Project '{project_name}' created in GitLab at: {project.web_url}")
        return project
    except gitlab.exceptions.GitlabCreateError as e:
        print(f"Failed to create project in GitLab: {e}")
        sys.exit(1)

def create_local_folder(project_name):
    """Create a local folder for the project."""
    project_dir = os.path.join(GITLAB_LOCAL_DIR, project_name)
    os.makedirs(project_dir, exist_ok=True)
    print(f"Created or verified local directory: {project_dir}")
    return project_dir

def create_readme(local_dir, project_name):
    """Create a README file in the local project directory."""
    readme_content = f"# {project_name}\n\nHello World from {project_name} project!"
    readme_path = os.path.join(local_dir, "README.md")
    with open(readme_path, "w") as readme_file:
        readme_file.write(readme_content)
    print(f"README file created at: {readme_path}")

def push_to_gitlab(local_dir, git_url):
    """Initialize a git repository, commit, and push the files to GitLab."""
    try:
        subprocess.run(["git", "init"], cwd=local_dir, check=True)
        subprocess.run(["git", "add", "."], cwd=local_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=local_dir, check=True)
        subprocess.run(["git", "branch", "-M", "main"], cwd=local_dir, check=True)
        subprocess.run(["git", "remote", "add", "origin", git_url], cwd=local_dir, check=True)
        subprocess.run(["git", "push", "-u", "origin", "main"], cwd=local_dir, check=True)
        print(f"Successfully pushed to GitLab repository: {git_url}")
    except subprocess.CalledProcessError as e:
        print(f"Git error occurred: {e}")
        sys.exit(1)

def open_in_vscode(local_dir):
    """Open the project folder in VS Code."""
    try:
        subprocess.run(["code", local_dir], check=True)
        print(f"VS Code opened for project: {local_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to open VS Code: {e}")

def setup_gitlab_project(project_name):
    """Complete setup for the GitLab project."""
    gl_client = initialize_gitlab()
    
    # Create project in GitLab
    gitlab_project = create_gitlab_project(gl_client, project_name)
    git_url = gitlab_project.http_url_to_repo
    
    # Set up local folder
    local_dir = create_local_folder(project_name)
    create_readme(local_dir, project_name)
    
    # Push to GitLab and open in VS Code
    push_to_gitlab(local_dir, git_url)
    open_in_vscode(local_dir)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 new_project.py <project_name>")
        sys.exit(1)
    
    project_name = sys.argv[1]
    setup_gitlab_project(project_name)