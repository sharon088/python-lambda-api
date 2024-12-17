# Python Scripts for GitLab & Google Sheets

This repository contains a collection of Python automation scripts designed to interact with GitLab and Google Sheets APIs.

## Features

1. **create_user.py**: Creates new GitLab user and repo based on data parsed from Google Sheets.
2. **csv_to_excel.py**: Converts CSV file into Excel file.
3. **get_info.py**: Appends Wikipedia topic's summary section into text file.
4. **backup.py**: Daily backups of files, auto clean to save latest file once a week & month.
5. **new_project.py**: Locally creates project's folder, pushes it to GitLab and opens it on VScode.
6. **send_whatsapp.py**: Sends whatsapp messages to predefined list of contacts in Google Sheets.

## Prerequisites
1. [Google Sheets API](https://developers.google.com/sheets/api/guides/concepts)
2. [Google Sheets - Python API](https://developers.google.com/sheets/api/quickstart/python)
3. [GitLab Server Setup](https://about.gitlab.com/install/)
4. [WhatsApp Web](https://web.whatsapp.com)

## Setup

1. Follow the instructions in `Prerequisites` guides. Make sure to enable `Google Sheet API` & `Google Drive API` in the google console.

2. Generate and Download the credentials.json File:
   * Go to `Credentials` tab in the console > `Service Accounts` > `Keys` > `Create New Key` > Select `JSON` as the key type and click `Create`.

   * Rename the file to `credentials.json` and save it in the same dir as the scripts.

   * Save the service account's email address for next step. Example address: my-service-account@your-project.iam.gserviceaccount.com

3. Create Google Sheets for the data to parse
    * **Python script GitLab**:

      | **Name**     | **Username** | **Email**            | **Password** |
      |--------------|--------------|----------------------|--------------|
      | John Doe     | johndoe      | johndoe@example.com  | password123  |
      | Jane Smith   | janesmith    | janesmith@example.com| password456  |

      ---
    * **Python script whatsapp**:

      | **Phone Number**  | **Message**                           |
      |-------------------|---------------------------------------|
      | +972123456789     | Hello, this is an automated message!  |
      | +972987654321     | This is another automated message.    |

    * **Share the Google Sheet with the Service Account**: Open both of your Google Sheets in your browser > Click on `Share` > Insert the `service account's email address` from previous step > Grant `Editor` permission.

4. Ensure you have the `credentials.json` file from Google Cloud Console for Sheets API access.

5. Create `docker-compose.yml` for your GitLab server and run it
   ```yaml
   services:
    gitlab:
      image: gitlab/gitlab-ce:latest
      container_name: gitlab
      restart: always
      hostname: gitlab.local
      environment:
        GITLAB_OMNIBUS_CONFIG: |
          external_url 'http://gitlab.local'
      ports:
        - "9090:80"
        - "443:443"
        - "2222:22"
      volumes:
        - gitlab_data:/var/opt/gitlab
        - gitlab_logs:/var/log/gitlab
        - gitlab_config:/etc/gitlab

   volumes:
     gitlab_data:
     gitlab_logs:
     gitlab_config:
   ```

   * Run `docker-compose up -d` to start the server
   * View the logs with `docker compose logs -f`
   * Go to `http://localhost:9090`
   * Username: admin
   * Password: `docker exec -it gitlab cat /etc/gitlab/initial_root_password`

6. Install requirements in virtual environment
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

7. Create `.env` file
   ```bash
   nano .env
   ```
   Insert the following environment variables:
   ```bash
   GITLAB_USERNAME=<your_gitlab.com_username>
   GITLAB_TOKEN=<your_gitlab.com_api_token>
   GITLAB_SERVER_USERNAME=<your_gitlab_server_username>
   GITLAB_SERVER_TOKEN=<your_gitlab_server_api_token>
   GROUP_ID=<your_gitlab_server_group_id>
   ```

## Usage

1. Run the script (Example uses)
   ```bash
   python3 create_user.py
   python3 csv_to_excel.py <path/to/csv_file.csv>
   python3 get_info.py <wikipedia_topic>
   python3 new_project.py <project_name>
   python3 send_whatsapp.py
   ``` 
2. Note that `backup.py` runs with Crontab
   ```bash
   crontab -e
   0 18 * * * /usr/bin/python3 /path/to/backup.py
   ``` 

## Cleanup

* Deactivate virtual environment with `deactivate` command.
* Stop GitLab's server container with `docker compose down`