import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from server.src.email.config import get_email_settings

settings = get_email_settings()

class EmailSender:
    def __init__(self, email, app_password):
        try:
            self.smtp = smtplib.SMTP(host="smtp.gmail.com", port="587")

            self.smtp.ehlo()
            self.smtp.starttls()
            self.smtp.login(email, app_password)
            self.email = email
        except Exception as e:
            print("Error message: ", e)

        pass

    def send_email(self, to_email, html_content, subject):
        try:
            content = MIMEMultipart()
            content["subject"] = subject
            content["from"] = self.email
            content["to"] = to_email
            content.attach(MIMEText(html_content, "html"))

            self.smtp.send_message(content)
        except Exception as e:
            print("Error message: ", e)

    def __del__(self):

        self.smtp.quit()
        pass


email_sender = EmailSender(
    settings.GMAIL_SENDER, settings.GMAIL_APP_PASSWORD)
