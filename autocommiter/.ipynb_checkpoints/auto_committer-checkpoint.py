import os
import subprocess
import schedule
import time
from datetime import datetime
# from dotenv import load_dotenv
# Load environment variables from a specified .env file
# load_dotenv(dotenv_path='/media/hanisntsolo/WDBlue_ssd_hanis/docker/volumes/jupyter/notebooks/.env') # Not is case of container
# Set your repository path
AUTO_COMMIT_REPO_PATH = str(os.getenv('AUTO_COMMIT_REPO_PATH'))
# Set your specific directory to add
COMMIT_SPECIFIC_DIRECTORY = str(os.getenv('COMMIT_SPECIFIC_DIRECTORY'))
# GitHub token and user/repo information
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
LAB_REPO_OWNER = os.getenv('LAB_REPO_OWNER')
LAB_REPO_NAME = os.getenv('LAB_REPO_NAME')
COMMITTER = os.getenv('COMMITTER')
USER_EMAIL = os.getenv('USEREMAIL')
USER_NAME = os.getenv('USERNAME')
INTERVAL = int(os.getenv('COMMIT_INTERVAL_SECONDS'))
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
        commit_message = f'Auto-commit on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} -[FROM-{COMMITTER}]- Regular update to keep the repository up-to-date.'

        # Commit changes
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)

        # Push changes using GitHub token
        push_command = [
            'git',
            'push',
            f'https://{GITHUB_TOKEN}@github.com/{LAB_REPO_OWNER}/{LAB_REPO_NAME}.git'
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
    subprocess.run(['git', 'config', '--global', '--add', 'safe.directory', COMMIT_SPECIFIC_DIRECTORY])
    # Set Git user info
    subprocess.run(['git', 'config', '--global', 'user.email', USER_EMAIL], check=True)
    subprocess.run(['git', 'config', '--global', 'user.name', USER_NAME], check=True)
    while True:
        time.sleep(INTERVAL)
        commit_and_push()
#chmod +x /path/to/your/auto_commit_with_token.py
#*/5 * * * * /usr/bin/python3 /media/hanisntsolo/WDBlue_ssd_hanis/docker/volumes/jupyter/notebooks/AutoAddAndCommit.py >> /media/hanisntsolo/WDBlue_ssd_hanis/docker/volumes/jupyter/notebooks/AutoAddAndCommit.log 2>&1
