from dotenv import load_dotenv
import os
import psutil
import time
import pytz
from datetime import datetime
from tuya_connector import TuyaOpenAPI

# Load environment variables
load_dotenv()

# Constants
LAPTOP_PLUG_ID = os.getenv("TUYA_LAPTOP_ID")
LOW_BATTERY_THRESHOLD = 40   # Turn on plug if battery is below this level
HIGH_BATTERY_THRESHOLD = 80  # Turn off plug if battery exceeds this level

# Get IST time
def get_ist_time():
    utc_now = datetime.now(pytz.utc)
    local_time_now = pytz.timezone('Asia/Kolkata')
    return utc_now.astimezone(local_time_now).strftime('%Y-%m-%d %H:%M:%S')

# Write logs
def write_log(message):
    print(f"{get_ist_time()} - [LAPTOP_SMART_PLUG] : {message}")

# Initialize Tuya API
def initialize_tuya_api():
    access_id = os.getenv("TUYA_ACCESS_ID")
    access_key = os.getenv("TUYA_ACCESS_KEY")
    if not all([access_id, access_key]):
        raise ValueError("Tuya credentials must be set as environment variables.")
    openapi = TuyaOpenAPI("https://openapi.tuyaus.com", access_id, access_key)
    openapi.connect()
    return openapi

# Get plug status
def get_plug_status(openapi):
    response = openapi.get(f"/v1.0/iot-03/devices/{LAPTOP_PLUG_ID}/status")
    if response.get("success"):
        return response.get("result")
    write_log(f"Failed to get plug status: {response}")
    return []

# Send command to plug
def send_tuya_command(openapi, command):
    payload = {"commands": [command]}
    response = openapi.post(f"/v1.0/iot-03/devices/{LAPTOP_PLUG_ID}/commands", payload)
    if response.get("success"):
        write_log("Plug command executed successfully")
    else:
        write_log(f"Failed to execute command: {response.get('msg')}")

# Check if plug is on
def is_plug_on(status):
    for item in status:
        if item['code'] == 'switch_1':
            return item['value']
    return False

# Monitor battery and control plug
def monitor_battery():
    openapi = initialize_tuya_api()

    while True:
        battery = psutil.sensors_battery()
        if not battery:
            write_log("Battery information not available")
            time.sleep(60)
            continue

        charge_percent = battery.percent
        is_charging = battery.power_plugged
        plug_status = get_plug_status(openapi)
        plug_on = is_plug_on(plug_status)

        write_log(f"Battery: {charge_percent}%, Charging: {is_charging}, Plug: {plug_on}")

        if charge_percent < LOW_BATTERY_THRESHOLD and not plug_on:
            write_log("Battery low, turning on plug.")
            send_tuya_command(openapi, {"code": "switch_1", "value": True})

        elif charge_percent >= HIGH_BATTERY_THRESHOLD and plug_on:
            write_log("Battery high, turning off plug.")
            send_tuya_command(openapi, {"code": "switch_1", "value": False})

        time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    monitor_battery()
