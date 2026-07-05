from datetime import datetime, time

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from quiz_app.mail import send_reminder_email


scheduler = BackgroundScheduler()
_app_instance = None


def send_reminders():
    """Find today's events with pending (unconfirmed) registrations
    and send a reminder to every team member."""
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
            ).all()

            for reg in pending_regs:
                team = Team.query.get(reg.team_id)
                if not team:
                    continue
                for member in team.members:
                    try:
                        send_reminder_email(member, event)
                        app.logger.info(
                            f"Scheduler: reminder sent to {member.email} "
                            f"for event '{event.name}'"
                        )
                    except Exception as e:
                        app.logger.error(
                            f"Scheduler: failed to send reminder "
                            f"to {member.email}: {e}"
                        )

        app.logger.info(
            f"Scheduler: processed {len(events)} event(s) today"
        )


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
    scheduler.start()
    app.logger.info("Scheduler started — daily reminders at 08:00")
