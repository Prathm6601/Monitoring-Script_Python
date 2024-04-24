import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

# Function to send email notification to multiple recipients
def send_email(subject, message, receiver_emails, downtime_info):
    sender_email = "prathamesh.patil@aitglobalinc.com"
    password = "myif cjni nuxj sdej"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ', '.join(receiver_emails)  # Join multiple emails with comma
    msg['Subject'] = subject

    # Include downtime information in the message
    message_with_downtime = f"{message}\n\n{downtime_info}"

    msg.attach(MIMEText(message_with_downtime, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_emails, text)  # Use receiver_emails instead of receiver_email
        server.quit()
        print("Email notification sent successfully!")
    except Exception as e:
        print("Failed to send email notification:", str(e))

# Function to check the status of the web service
def check_service(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"{url} is UP!")
            return True
        else:
            print(f"{url} is DOWN!")
            return False
    except Exception as e:
        print(f"Failed to connect to {url}: {str(e)}")
        return False

# Main function to monitor web services
def monitor_services(services, interval, receiver_emails):
    while True:
        for service, url in services.items():
            if not check_service(url):
                subject = f"{service} is down!"
                message = f"The service {service} ({url}) is currently down."
                downtime_info = f"This {service} will be down for 2 minutes because of a background deployment pipeline running. After the 2 minutes, it should be back up."
                send_email(subject, message, receiver_emails, downtime_info)  # Pass receiver_emails and downtime_info
        time.sleep(interval)

# Define your web services and their URLs
services = {
    "Service 1": "https://niradev.aitglobalindia.com/",
    "Service 2": "https://niraqa.aitglobalindia.com/",
    "Service 3": "https://nirauat.aitglobalindia.com/",
}

# Set the interval (in seconds) for checking the services
interval = 60  # Check every minute

# Define multiple receiver emails
receiver_emails = ["prathamesh.patil@aitglobalinc.com", "amol.funde@aitglobalinc.com", "saurabh.bhalerao@aitglobalinc.com", "nilesh.patil@aitglobalinc.com", "hamid.obaid@aitglobalinc.com", "shantesh.varnal@aitglobalinc.com"]

# Start monitoring the services
monitor_services(services, interval, receiver_emails)
