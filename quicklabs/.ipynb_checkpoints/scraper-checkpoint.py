import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
import time
import os
# Parameters: length of each code and number of codes to generate
code_length = 10
number_of_codes = 1

LOG_FILE_PATH = '/home/jovyan/work/jupyter-lab/quicklabs/scraper.log'

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
        
def generate_codes(length, count):
    # Character set: lowercase letters and digits
    charset = string.ascii_lowercase + string.digits
    # Generate unique codes
    codes = set()
    code = ''.join(random.choice(charset) for _ in range(length))
    return code
    
def send_email(subject, body, to_email):
    # Email configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "ds.pratap1997@gmail.com"  # Replace with your email
    sender_password = "xxxxxxxxxxxx"      # Replace with your email password

    try:
        # Create the email
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject

        # Attach the email body
        msg.attach(MIMEText(body, "plain"))

        # Send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())

        write_log(f"Email sent to {to_email}.")
    except Exception as e:
        write_log(f"Failed to send email: {e}")

def check_text_in_url(url, text_to_find, coupon, recipient_email):
    try:
        # Send a GET request to the URL
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP status codes 4xx/5xx

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        if text_to_find == "applied":
            if text_to_find in soup.get_text():
                subject = f"{coupon}: Code can be used!"
                write_log(subject)
                body = f"{text_to_find} was not found in the HTML content of {url}"
                write_log(f"{text_to_find} SUCCESS {url}.")
        
                # Send an email notification
                send_email(subject, body, recipient_email)
        
        if text_to_find not in soup.get_text():                
            write_log(f"{text_to_find} found in the HTML content of {url}")
            # Check for another text within the same block
        elif text_to_find not in soup.get_text():
            write_log(f"{another_text} found in the HTML content of {url}")
        else:
            # Handle the case when text_to_find is not present
            subject = f"{coupon}: Code can be used!"
            print(subject)
            body = f"{text_to_find} was not found in the HTML content of {url}"
            write_log(f"{text_to_find} SUCCESS {url}.")
    
            # Send an email notification
            send_email(subject, body, recipient_email)
    
    except requests.exceptions.RequestException as e:
        write_log(f"An error occurred while fetching the URL: {e}")

if __name__ == "__main__":
    # Example usage
    recipient_email = "ds.pratap1997@gmail.com"  # Replace with the recipient's email
    while True:
        text_to_search = "Coupon usage limit has been reached"
        coupon = generate_codes(code_length, number_of_codes)
        url_to_check = "https://whitesquarein.com/googlecloudarcade/product/champions-milestone-package/?get=ar" + coupon 
        check_text_in_url(url_to_check, text_to_search, coupon, recipient_email)
        # Check if the text is present in the HTML
        text_to_search = f"\"{coupon}\""
        url_to_check = "https://whitesquarein.com/googlecloudarcade/product/premium-plus/?get=ar" + coupon 
        check_text_in_url(url_to_check, text_to_search, coupon, recipient_email)
        text_to_serch = "applied"
        url_to_check = "https://whitesquarein.com/googlecloudarcade/product/premium-plus/?get=ar" + coupon 
        check_text_in_url(url_to_check, text_to_search, coupon, recipient_email)
        url_to_check = "https://whitesquarein.com/googlecloudarcade/product/champions-milestone-package/?get=ar" + coupon 
        check_text_in_url(url_to_check, text_to_search, coupon, recipient_email)
        time.sleep(5)
