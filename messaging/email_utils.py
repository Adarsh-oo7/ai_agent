import smtplib
from email.message import EmailMessage

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 465
EMAIL_USER = "your-email@gmail.com"
EMAIL_PASS = "your-app-password"

def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
