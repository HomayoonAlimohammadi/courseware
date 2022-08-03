from __future__ import annotations
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from django.core.mail import send_mail
from django.conf import settings


class ContactSupportException(Exception):
    pass


class EmailSender:
    def __init__(
        self,
        support_email: str,
        support_password: str,
        customer_email: str,
        title: str,
        text: str,
    ):

        self.support_email = support_email
        self.support_password = support_password
        self.customer_email = customer_email
        self.title = title
        self.text = text
        self.login_to_email()

    def login_to_email(self) -> None:
        email = self.support_email
        password = self.support_password
        session = smtplib.SMTP("smtp.gmail.com", 587)
        session.ehlo()
        session.starttls()
        session.login(email, password)
        self.session: smtplib.SMTP = session

    def configure_email_message(self) -> MIMEMultipart:
        subject = self.title
        message = MIMEMultipart()
        message["From"] = self.support_email
        message["To"] = self.customer_email
        message["Subject"] = subject
        mail_content = self.text
        message.attach(MIMEText(mail_content, "html"))
        return message

    def send_email(self) -> None:
        message = self.configure_email_message()
        text = message.as_string()
        self.session.sendmail(self.support_email, self.customer_email, text)
        self.session.quit()


def send_email_to_support_manual(
    title: str | None,
    text: str | None,
    customer_email: str | None,
    support_email: str = "danial@divar.com",
):
    try:
        with open("credentials.json", "r") as f:
            data = json.load(f)
            support_email = data.get("support_email")
            support_password = data.get("support_password")

        email_sender = EmailSender(
            title=title,  # type: ignore
            text=text,  # type: ignore
            customer_email=customer_email,  # type: ignore
            support_email=support_email,
            support_password=support_password,
        )
        email_sender.send_email()
    except Exception as e:
        print(e)
        raise ContactSupportException


def send_email_to_support(
    subject: str,
    message: str,
    recipient: str,
):
    subject = subject
    message = message
    recipient_list = [recipient]
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=recipient_list,
        )
    except Exception as e:
        print(e)  # This should be replaces with logging system.
        raise ContactSupportException
