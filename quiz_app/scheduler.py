from datetime import datetime, time, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from quiz_app.mail import send_reminder_email


scheduler = BackgroundScheduler()
_app_instance = None


def send_reminders():
    """Find today's events with pending (unconfirmed) registrations
    and send a reminder to every team member exactly once per registration."""
    from quiz_app import db
    from quiz_app.models import Event, RegistrationsEvent, Team

    app = _app_instance
    if not app:
        return

    with app.app_context():
        today = datetime.now().date()
        events = Event.query.filter(
            Event.date >= datetime.combine(today, time.min),
            Event.date < datetime.combine(today, time.max),
        ).all()

        if not events:
            app.logger.info("Scheduler: no events today")
            return

        for event in events:
            pending_regs = RegistrationsEvent.query.filter(
                RegistrationsEvent.event_id == event.id,
                RegistrationsEvent.status == "pending",
                RegistrationsEvent.waitlist == False,
                RegistrationsEvent.reminder_sent_at.is_(None),
            ).all()

            for reg in pending_regs:
                team = Team.query.get(reg.team_id)
                if not team:
                    continue
                sent = False
                for member in team.members:
                    try:
                        send_reminder_email(member, event)
                        app.logger.info(
                            f"Scheduler: reminder sent to {member.email} "
                            f"for event '{event.name}'"
                        )
                        sent = True
                    except Exception as e:
                        app.logger.error(
                            f"Scheduler: failed to send reminder "
                            f"to {member.email}: {e}"
                        )
                if sent:
                    reg.reminder_sent_at = datetime.now()

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

        app.logger.info(
            f"Scheduler: processed {len(events)} event(s) today"
        )


def cleanup_pending_registrations():
    """Auto-remove unconfirmed registrations whose 13:00 deadline has passed.

    Runs every day at 13:00 so the "registration cancelled" emails
    are always sent by the deadline, even if nobody visits the site."""
    from quiz_app.blueptints.api import auto_cleanup_pending

    app = _app_instance
    if not app:
        return

    with app.app_context():
        auto_cleanup_pending()
        app.logger.info("Scheduler: pending registrations cleanup finished")


def cleanup_old_events():
    """Delete events older than 6 months and their associated files."""
    from quiz_app import db
    from quiz_app.models import Event
    import os
    from flask import current_app

    app = _app_instance
    if not app:
        return

    with app.app_context():
        six_months_ago = datetime.now() - timedelta(days=180)
        old_events = Event.query.filter(Event.date < six_months_ago).all()

        if not old_events:
            return

        for e in old_events:
            if e.photo:
                photo_path = os.path.join(app.root_path, "media", e.photo)
                if os.path.exists(photo_path):
                    os.remove(photo_path)
            db.session.delete(e)

        try:
            db.session.commit()
            app.logger.info(f"Scheduler: cleaned up {len(old_events)} old event(s)")
        except Exception:
            db.session.rollback()
            app.logger.error("Scheduler: failed to clean up old events")


def init_scheduler(app):
    """Initialize and start the background scheduler."""
    global _app_instance
    _app_instance = app

    if scheduler.running:
        return

    trigger = CronTrigger(hour=8, minute=0)
    scheduler.add_job(
        send_reminders,
        trigger=trigger,
        id="send_daily_reminders",
        replace_existing=True,
    )
    scheduler.add_job(
        cleanup_pending_registrations,
        trigger=CronTrigger(hour=13, minute=0),
        id="cleanup_pending_registrations",
        replace_existing=True,
    )
    scheduler.add_job(
        cleanup_old_events,
        trigger=CronTrigger(hour=3, minute=0),
        id="cleanup_old_events",
        replace_existing=True,
    )
    scheduler.start()
    app.logger.info("Scheduler started — daily reminders at 08:00, cleanup at 03:00/13:00")


def run_jobs_once(app):
    """Run the scheduled jobs once, without starting a background scheduler.

    Used from a cron job on shared hosting (Рег.ру / ispmanager),
    where APScheduler inside a Passenger process would duplicate work.
    """
    global _app_instance
    _app_instance = app
    with app.app_context():
        send_reminders()
        cleanup_pending_registrations()
        cleanup_old_events()
