from __future__ import annotations
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from django.core.mail import send_mail
from django.conf import settings
from uuid import uuid4
import core.models as models
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.conf import settings
from django.core.mail import send_mail, BadHeaderError


class ContactSupportException(Exception):
    pass


class PasswordResetEmailException(Exception):
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
    support_email: str = "ostadju@fastmail.com",
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
    customer_email: str,
):
    subject = subject
    message = message
    recipient_list = [settings.SUPPORT_EMAIL]
    subject += f"\nThis Email was sent from {customer_email}."
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


def send_password_reset_email(request, user):
    subject = "Password Reset Requested"
    email_template = "password/reset_email.txt"
    if request.is_secure():
        protocol = "https://"
    else:
        protocol = "http://"
    content_map = {
        "username": user.username,
        "email": user.email,
        "domain": request.get_host(),
        "site_name": "Courseware",
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "user": user,
        "token": default_token_generator.make_token(user),
        "protocol": protocol,
    }
    email_text = render_to_string(email_template, content_map)
    try:
        send_mail(
            subject=subject,
            message=email_text,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
        )
    except BadHeaderError:
        raise PasswordResetEmailException


def uuid_namer(instance, file_name: str) -> str:
    name, ext = file_name.split(".")
    return f"{name}_{str(uuid4())}.{ext}"


def interval_has_overlap(
    intervals: list[models.Interval], new_interval: models.Interval
) -> bool:
    """Returns `True` if the `new_interval` overlaps with current `intervals` of the `teacher`. If not, returns `False`."""
    for interval in intervals:
        if interval.day != new_interval.day:
            continue
        # ref:  (   )
        # new:    (     )
        if (
            new_interval.start_time < interval.end_time
            and new_interval.start_time >= interval.start_time
        ):
            return True
        # ref:  (    )
        # new: (   )
        if (
            new_interval.end_time <= interval.end_time
            and new_interval.end_time >= interval.start_time
        ):
            return True
        # The two above also include:
        # ref  (     )
        # new:   (  )

        # ref :     (   )
        # new:    (       )
        if (
            new_interval.start_time <= interval.start_time
            and new_interval.end_time >= interval.end_time
        ):
            return True
    return False
