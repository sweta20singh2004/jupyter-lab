import os
import subprocess
import schedule
import time
from datetime import datetime

# ########################################################
# Run to install schedule package on your machine
# pip install schedule
# CRON SETUP
#chmod +x /path/to/your/auto_commit_with_token.py
#*/5 * * * * /usr/bin/python3 /mnt/8AB0DDCFB0DDC1BD/docker/volumes/jupyter/notebooks/AutoAddAndCommit.py >> /mnt/8AB0DDCFB0DDC1BD/docker/volumes/jupyter/notebooks/AutoAddAndCommit.log 2>&1
# ########################################################

# Set your repository path
REPO_PATH = '/mnt/8AB0DDCFB0DDC1BD/docker/volumes/jupyter/notebooks/jupyter-lab'

# Set your specific directory to add
SPECIFIC_DIRECTORY = '/mnt/8AB0DDCFB0DDC1BD/docker/volumes/jupyter/notebooks/jupyter-lab'

# GitHub token and user/repo information
GITHUB_TOKEN = '<token>' # Your github token
REPO_OWNER = '<github-username/ownername>' # sweta20singh2004
REPO_NAME = 'jupyter-lab'

# Path to your log file
LOG_FILE_PATH = '/mnt/8AB0DDCFB0DDC1BD/docker/volumes/jupyter/notebooks/AutoAddAndCommit.log'

def write_log(message):
    try:
        # Read the existing contents of the log file
        if os.path.exists(LOG_FILE_PATH):
            with open(LOG_FILE_PATH, 'r') as file:
                existing_content = file.read()
        else:
            existing_content = ''

        # Prepend the new log entry
        with open(LOG_FILE_PATH, 'w') as file:
            file.write(f"{message}\n{existing_content}")

    except Exception as e:
        print(f'Error occurred while writing to log file: {e}')

def commit_and_push():
    try:
        # Change directory to the repository path
        os.chdir(REPO_PATH)

        # Add changes from the specific directory
        subprocess.run(['git', 'add', SPECIFIC_DIRECTORY], check=True)
        # Pull to check latest changes from the specific directory
        subprocess.run(['git', 'pull'], check=True)

        # Create commit message with the latest date and time
        commit_message = f'Auto-commit on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Regular update to keep the repository up-to-date.'

        # Commit changes
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)

        # Push changes using GitHub token
        push_command = [
            'git',
            'push',
            f'https://{GITHUB_TOKEN}@github.com/{REPO_OWNER}/{REPO_NAME}.git'
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

