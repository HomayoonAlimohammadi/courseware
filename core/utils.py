from __future__ import annotations


class ContactSupportException(Exception):
    pass


def send_email_to_support(
    title: str | None,
    text: str | None,
    user_email: str | None,
    support_email: str = "danial@divar.com",
):
    try:
        pass
    except Exception as e:
        print(e)
        raise ContactSupportException
