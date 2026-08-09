import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask import current_app, render_template


def send_email(to, subject, html_body):
    """Send an HTML email via Yandex SMTP."""
    smtp_server = current_app.config.get("MAIL_SERVER", "smtp.yandex.ru")
    smtp_port = current_app.config.get("MAIL_PORT", 465)
    username = current_app.config.get("MAIL_USERNAME")
    password = current_app.config.get("MAIL_PASSWORD")
    sender = current_app.config.get("MAIL_DEFAULT_SENDER", username)

    if not password:
        current_app.logger.warning("MAIL_PASSWORD not configured, skipping email")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"TLTQUIZ <{sender}>"
    msg["To"] = to

    text_part = MIMEText(html_body, "html", "utf-8")
    msg.attach(text_part)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(username, password)
            server.sendmail(sender, to, msg.as_string())
        current_app.logger.info(f"Email sent to {to}: {subject}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email to {to}: {e}")
        return False


def send_welcome_email(user):
    """Send welcome email after registration."""
    html = render_template("emails/welcome.html", user=user)
    send_email(user.email, "Добро пожаловать в TLTQUIZ!", html)


def send_registration_confirmed_email(user, event):
    """Send email when registration is confirmed."""
    html = render_template("emails/registration_confirmed.html", user=user, event=event)
    send_email(user.email, f"Участие подтверждено — {event.name}", html)


def send_reminder_email(user, event):
    """Send reminder email on event day — confirm participation before 13:00."""
    html = render_template("emails/reminder.html", user=user, event=event)
    send_email(user.email, f"Напоминание: {event.name} сегодня!", html)


def send_password_reset_email(user, code):
    """Send password reset code email."""
    html = render_template("emails/reset_password.html", user=user, code=code)
    send_email(user.email, "Код для сброса пароля — TLTQUIZ", html)


def send_registration_removed_email(user, event, reason):
    """Send email when registration is removed by admin or auto-cleanup."""
    html = render_template("emails/registration_removed.html", user=user, event=event, reason=reason)
    send_email(user.email, f"Регистрация отменена — {event.name}", html)
