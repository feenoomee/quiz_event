from unittest.mock import patch

from quiz_app.mail import send_email


def test_email_delivery_is_disabled_by_default(app):
    with app.app_context(), patch("quiz_app.mail.smtplib.SMTP_SSL") as smtp:
        sent = send_email("user@example.com", "Test", "<p>Test</p>")

    assert sent is False
    smtp.assert_not_called()
