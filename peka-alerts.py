import requests
from bs4 import BeautifulSoup
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
import os

url = 'https://peka.ab.ca/canmore-rentals'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

#E-mail credentials
smtp_server = 'smtp.gmail.com'
smtp_port = 587
email_user = 'wadeembury@gmail.com'
#to_email = 'mwembury@gmail.com'
to_email = 'andrewtkan@gmail.com'


def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        email_password = os.environ.get('EMAIL_PASSWORD')
        if email_password is None:
            raise ValueError("Email password environment variable not set")
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_password)
        text = msg.as_string()
        server.sendmail(email_user, to_email, text)
        server.quit()
        print(f"Email sent to {to_email}!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def check_for_text(url, headers, search_texts):
    try:
        response = requests.get(url)
        response.raise_for_status()

        if response.status_code == 200:
            print("Successfully got the website.")
            soup = BeautifulSoup(response.content, 'html.parser')

            found_texts = []
            for text in search_texts:
                if soup.find_all(string=lambda s:text in s):
                    found_texts.append(text)

            if found_texts:
                for text in found_texts:
                    print(f"Alert: '{text}' is present on page")
                    send_email(f"Alert: New Listing for '{text}' Found!", f"There is a new listing at {url} with the contents '{text}'! Join the commune, become one of the Vue Crew")
                    update_last_sent_time()
            else:
                print(f"No matching text found on the page")

        else:
            print("Failed to find website: reponse.status_code")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurreddd: {http_err}")
    except Exception as err:
        print(f"An error occurredddd: {err}")


def is_past_24_hours(last_sent_time):
    now = datetime.datetime.now()
    time_diff = now - last_sent_time
    return time_diff.total_seconds() >= 24 * 3600

def update_last_sent_time():
    now = datetime.datetime.now()
    with open("last_sent_time.txt", "w") as file:
        file.write(now.isoformat())

def get_last_sent_time():
    if os.path.exists("last_sent_time.txt"):
        with open("last_sent_time.txt", "r") as file:
            last_sent_time_str = file.read().strip()
            return datetime.datetime.fromisoformat(last_sent_time_str)
    else:
        return None

if __name__ == "__main__":
    search_texts = ["Rundle House", "rundle house", "RUNDLE HOUSE", "Rundlehouse", "rundlehouse", "Vue", "VUE", "vue", "Kananaskis Way"]
    while True:
        last_sent_time = get_last_sent_time()

        if last_sent_time is None or is_past_24_hours(last_sent_time):
            print ("No e-mail sent today. Checking for text matches to the site")
            check_for_text(url, headers, search_texts)
        else:
            print("Skipping email sending, as an email was already sent within the past 24 hours.")
        print("Waiting 30 minutes before next check...")
        time.sleep(1800)
    