import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv(dotenv_path="utils/.env")

# Email account credentials
EMAIL = os.getenv("RECEIVER-EMAIL")
PASSWORD = os.getenv("RECEIVER-PASSWORD")
TO_EMAIL = os.getenv("TO-EMAIL")
CC_EMAIL = os.getenv("CC-EMAIL")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_email(subject, attachment_path):
    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = TO_EMAIL
    msg["Cc"] = CC_EMAIL
    msg["Subject"] = subject
    
    msg.attach(MIMEText("Please find the requested catalogue attached.", "plain"))

    # Attach the PDF file
    with open(attachment_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {os.path.basename(attachment_path)}",
        )
        msg.attach(part)

    recipients = [TO_EMAIL] + [CC_EMAIL]

    # Send the email
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, recipients, msg.as_string())
    
    # Delete the PDF file
    os.remove(attachment_path)