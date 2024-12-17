import os
import shutil
import datetime

BACKUP_DIR = "./outputs/backups"
SOURCE_FILES = ["./outputs/wikipedia.txt"]  # List of files

os.makedirs(BACKUP_DIR, exist_ok=True)

def create_backup():
    """ Creates a daily backup of the specified files """
    now = datetime.datetime.now()
    date_str = now.strftime("%d-%m-%Y")
    
    for file in SOURCE_FILES:
        if os.path.exists(file):
            file_name, file_ext = os.path.splitext(file)
            backup_name = f"{file_name}_{date_str}{file_ext}"
            backup_path = os.path.join(BACKUP_DIR, backup_name)
            shutil.copy(file, backup_path)
            print(f"Backed up {file} to {backup_path}")
        else:
            print(f"Source file '{file}' not found.")

def cleanup_weekly_monthly():
    """ Keeps only the latest backup of the week (Saturday) for each file """
    now = datetime.datetime.now()
    tomorrow = now + datetime.timedelta(days=1)
    if now.weekday() == 5 or tomorrow.month != now.month:  # Saturday or last day of the month
        backups = os.listdir(BACKUP_DIR)
        files_by_name = {}
        
        for backup in backups:
            base_name = "_".join(backup.split("_")[:-1])
            files_by_name.setdefault(base_name, []).append(backup)
        
        for base_name, file_list in files_by_name.items():
            file_list.sort(key=lambda f: datetime.datetime.strptime(f.split("_")[-1].split(".")[0], "%d-%m-%Y"))
            for file_to_delete in file_list[:-1]:
                os.remove(os.path.join(BACKUP_DIR, file_to_delete))
                print(f"Deleted weekly/monthly backup: {file_to_delete}")

create_backup()
cleanup_weekly_monthly()