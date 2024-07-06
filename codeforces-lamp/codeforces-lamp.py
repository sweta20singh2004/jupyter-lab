from dotenv import load_dotenv
import os
import hashlib
import random
import string
import time
import requests
from tuya_connector import TuyaOpenAPI
from datetime import datetime
from pprint import pp

def initialize_tuya_api():
    access_id = os.getenv("TUYA_ACCESS_ID")
    access_key = os.getenv("TUYA_ACCESS_KEY")
    if not all([access_id, access_key]):
        raise ValueError("Tuya credentials must be set as environment variables.")
    openapi = TuyaOpenAPI("https://openapi.tuyaus.com", access_id, access_key)
    openapi.connect()
    return openapi
    
def send_tuya_command(openapi, endpoint, commands):
    response = openapi.post(endpoint, commands)
    if response.get("success"):
        write_log("Bulb turned on successfully")
    else:
        write_log(f"Failed to execute command: {response.get('msg')}")
        
def calculate_sha512(text):
    return hashlib.sha512(text.encode('utf-8')).hexdigest()

def add_authorization_parameters(method, parameters, key, secret):
    parameters["apiKey"] = key
    parameters["time"] = str(int(time.time()))

    rand = ''.join(random.choices(string.ascii_lowercase, k=6))
    
    sorted_params = sorted(parameters.items())
    query_string = '&'.join(f'{k}={v}' for k, v in sorted_params)
    
    api_sig_base = f"{rand}/{method}?{query_string}#{secret}"
    api_sig = rand + calculate_sha512(api_sig_base)
    
    parameters["apiSig"] = api_sig

# Load environment variables from a specified .env file
load_dotenv(dotenv_path='/.env')

# Path to your log file
LAB_LOG_FILE_PATH = os.getenv('LAB_LOG_FILE_PATH')

def write_log(message):
    log_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [CODEFORCES_LAMP] : {message}"
    print(log_message)
    return # When inside container.
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

def codeforces_api_request(method, parameters):
    base_url = "https://codeforces.com/api/"
    url = f"{base_url}{method}"
    if not parameters:
        parameters = {}
    key = os.getenv("CODEFORCES_API_KEY")
    secret = os.getenv("CODEFORCES_API_SECRET")
    if not key or not secret:
        raise ValueError("API key and secret must be set as environment variables.")
    
    add_authorization_parameters(method, parameters, key, secret)
    
    combined_parameters = '&'.join(f'{k}={v}' for k, v in parameters.items())
    full_url = f"{url}?{combined_parameters}"
    # pp(f"Parameters before :: {parameters}")  # For debugging
    # pp(f"New Combined Parameters are :: {combined_parameters}")  # For debugging
    # pp(f"Formed Request is as follows :: {full_url}")  # For debugging
    response = requests.get(full_url)
    if response.status_code == 200:
        return response.json()
    else:
        write_log(f"Failed to fetch data: {response.get('msg')}")
        return None
        
def map_rating_to_color(rating):
    if rating < 1200:
        return {"h": 240, "s": 1000, "v": 1000}  # Blue
    elif rating < 1400:
        return {"h": 120, "s": 1000, "v": 1000}  # Green
    elif rating < 1600:
        return {"h": 180, "s": 1000, "v": 1000}  # Cyan
    elif rating < 1900:
        return {"h": 60, "s": 1000, "v": 1000}   # Yellow
    elif rating < 2100:
        return {"h": 30, "s": 1000, "v": 1000}   # Orange
    else:
        return {"h": 0, "s": 1000, "v": 1000}    # Red
        
def set_bulb_color(openapi, color):
    bulb_id = os.getenv("TUYA_BULB_ID")
    if not bulb_id:
        raise ValueError("Tuya bulb ID must be set as an environment variable.")
    
    commands = {
        "commands": [
            {"code": "switch_led", "value": True},
            {"code": "bright_value_v2", "value": 1000},
            {"code": "colour_data_v2", "value": color}
        ]
    }
    
    send_tuya_command(openapi, f"/v1.0/iot-03/devices/{bulb_id}/commands", commands)
    
def set_bulb_off(openapi):
    bulb_id = os.getenv("TUYA_BULB_ID")
    if not bulb_id:
        raise ValueError("Tuya bulb ID must be set as an environment variable.")
    
    commands = {
        "commands": [
            {"code": "switch_led", "value": False}
        ]
    }
    
    send_tuya_command(openapi, f"/v1.0/iot-03/devices/{bulb_id}/commands", commands)    
    
def contest_status(contestId, handle, asManager=False, submissionReturn=None, count=None):
    if not contestId:
        raise ValueError("ContestId must be provided")
    contestId = str(contestId)
    method = "contest.status"
    parameters = {}
    parameters["contestId"] = contestId
    if handle:
        parameters["handle"] = handle
    if asManager:
        parameters["asManager"] = asManager
    if submissionReturn:
        parameters["from"] = submissionReturn
    if count:
        parameters["count"] = count
    data = codeforces_api_request(method, parameters)
    return data
    
def contest_list():
    method = "contest.list"
    return codeforces_api_request(method, {})

def recent_submissions(count=None):
    if not count:
        count = 1
    method = "problemset.recentStatus"
    parameters = {}
    parameters["count"] = count
    return codeforces_api_request(method, parameters)
def user_info(handle="hanisntsolo"):
    method = "user.info"
    parameters = {"handles": handle}
    return codeforces_api_request(method, parameters)

def user_status(handle="hanisntsolo", count=1, tillFrom=1):
    method = "user.status"
    parameters = {}
    parameters["handle"] = handle
    parameters["from"] = tillFrom
    parameters["count"] = count
    return codeforces_api_request(method, parameters)
    
def codeforces_monitor_all_submissions():
    data = user_status()
    return data["result"][0]
    
def codeforces_submission_monitor():
    last_submission_timestamp = None
    last_submission_id = None
    openapi = initialize_tuya_api() # Set tupy api to be able to send instructions.
    while True:
        latest_submission = codeforces_monitor_all_submissions()
        write_log(pp(latest_submission))
        if latest_submission:
            submission_id = latest_submission["id"]
            submission_timestamp = latest_submission["creationTimeSeconds"]
            if(last_submission_id is None or submission_id > last_submission_id) and (last_submission_timestamp is None or submission_timestamp > last_submission_timestamp):
                write_log(f"New submission recorded : {submission_id}")
                # Process the submission and update bulb colorabs
                verdict = latest_submission["verdict"]
                process_submission(openapi)
                if verdict == "OK":
                    sleep_seconds = 120
                    accepted_log = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Verdict Accepted for submission : {submission_id}]"
                    write_log(accepted_log)
                    color = map_rating_to_color(1201)
                    set_bulb_color(openapi, color)
                    time.sleep(sleep_seconds)
                else:
                    sleep_seconds = 30
                    failure_log = f"{datetime.now().strftime('%y-%m-%d %H:%M:%S')} - [Verdict failure for submission : {submission_id}] : {pp(latest_submission)}"
                    write_log(failure_log)
                    color = map_rating_to_color(2101)
                    set_bulb_color(openapi, color)
                    time.sleep(sleep_seconds)
                #Update last processed submission timestamp or Idabs
                last_submission_timestamp = submission_timestamp
                last_submission_id = submission_id
            
            else:
                #No new submission, default to profile color
                data = user_info()
                if data:
                    user = data['result'][0]
                    rating = user['rating']
                    color = map_rating_to_color(rating)
                    set_bulb_color(openapi, color)
                    
        sleep_seconds = 5
        sleep_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Sleeping for : {sleep_seconds}]" 
        write_log(sleep_message)
        time.sleep(sleep_seconds) # Check for new submission every 5 seconds.
                    
def process_submission(openapi):
    color = map_rating_to_color(1901)
    for _ in range(3): # Number of blinks
        set_bulb_color(openapi, color)
        time.sleep(1)
        set_bulb_color(openapi, {"h": 0, "s": 0, "v": 0}) # Turn the bulb off
        time.sleep(1)
        
def main():
    codeforces_submission_monitor()
    
if __name__ == "__main__":
    main()

    
#chmod +x /media/hanisntsolo/WDBlue_ssd_hanis/docker/volumes/jupyter/notebooks/codeforces-lamp.py
#0 19 * * * /usr/bin/python3 /media/hanisntsolo/WDBlue_ssd_hanis/docker/volumes/jupyter/notebooks/codeforces-lamp.py >> /media/hanisntsolo/WDBlue_ssd_hanis/docker/volumes/jupyter/notebooks/AutoAddAndCommit.log 2>&1
