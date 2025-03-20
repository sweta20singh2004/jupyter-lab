import os
import subprocess
import schedule
import time
from datetime import datetime
from dotenv import load_dotenv
# Load environment variables from a specified .env file
load_dotenv(dotenv_path='/mnt/raid1/docker/volumes/jupyter/notebooks/.env')
# Set your repository path
AUTO_COMMIT_REPO_PATH = str(os.getenv('AUTO_COMMIT_REPO_PATH'))
# Set your specific directory to add
COMMIT_SPECIFIC_DIRECTORY = str(os.getenv('COMMIT_SPECIFIC_DIRECTORY'))
# GitHub token and user/repo information
GITHUB_TOKEN_SWETA = os.getenv('GITHUB_TOKEN_SWETA')
LAB_REPO_OWNER = os.getenv('LAB_REPO_OWNER')
LAB_REPO_NAME = os.getenv('LAB_REPO_NAME')

# Path to your log file
LAB_LOG_FILE_PATH = os.getenv('LAB_LOG_FILE_PATH')

def write_log(message):
    try:
        # Read the existing contents of the log file
        if os.path.exists(LAB_LOG_FILE_PATH):
            with open(LAB_LOG_FILE_PATH, 'r') as file:
                existing_content = file.read()
        else:
            existing_content = ''

        # Prepend the new log entry
        with open(LAB_LOG_FILE_PATH, 'w') as file:
            file.write(f"{message}\n{existing_content}")

    except Exception as e:
        print(f'Error occurred while writing to log file: {e}')

def commit_and_push():
    try:
        # Change directory to the repository path
        os.chdir(AUTO_COMMIT_REPO_PATH)

        # Add changes from the specific directory
        subprocess.run(['git', 'add', COMMIT_SPECIFIC_DIRECTORY], check=True)
        # Pull to check latest changes from the specific directory
        subprocess.run(['git', 'pull'], check=True)

        # Create commit message with the latest date and time
        commit_message = f'Auto-commit on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Regular update to keep the repository up-to-date.[FROM-SINGHSERVER]'

        # Commit changes
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)

        # Push changes using GitHub token
        push_command = [
            'git',
            'push',
            f'https://{GITHUB_TOKEN_SWETA}@github.com/{LAB_REPO_OWNER}/{LAB_REPO_NAME}.git'
        ]
        subprocess.run(push_command, check=True)

        log_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [SUCCESS] Changes committed and pushed successfully."
        print(log_message)
        write_log(log_message)

    except subprocess.CalledProcessError as e:
        log_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [ERROR] Error occurred: {e}"
        print(log_message)
        write_log(log_message)

if __name__ == "__main__":
    commit_and_push()
#chmod +x /path/to/your/auto_commit_with_token.py
#*/5 * * * * /usr/bin/python3 /media/hanisntsolo/WDBlue_ssd_hanis/docker/volumes/jupyter/notebooks/AutoAddAndCommit.py >> /media/hanisntsolo/WDBlue_ssd_hanis/docker/volumes/jupyter/notebooks/AutoAddAndCommit.log 2>&1
