"""macOS notification system using osascript (no extra dependencies)."""

import subprocess
import sys


def send_notification(title: str, message: str, sound: str = "default"):
    """Send a macOS notification using osascript."""
    if sys.platform != "darwin":
        print(f"[Notification] {title}: {message}")
        return

    script = (
        f'display notification "{_escape(message)}" '
        f'with title "{_escape(title)}" '
        f'sound name "{sound}"'
    )
    try:
        subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            timeout=5,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        # Fallback: just print
        print(f"[Notification] {title}: {message}")


def send_monthly_reminder(partner_name: str):
    send_notification(
        "Gift Reminder \U0001f490",
        f"Time for a small gift for {partner_name}! Open the app for personalized suggestions.",
    )


def send_quarterly_reminder(partner_name: str):
    send_notification(
        "Surprise Gift Time! \u2728",
        f"Quarterly surprise for {partner_name} is due. Check out some special ideas!",
    )


def send_update_reminder():
    send_notification(
        "6-Month Check-In \U0001f504",
        "Time for a quick update to keep your gift suggestions fresh and relevant.",
    )


def check_and_notify(db):
    """Check for due reminders and send notifications."""
    profile = db.get_profile()
    if not profile:
        return

    partner_name = profile["partner_name"]
    due = db.get_due_reminders()

    for reminder in due:
        rtype = reminder["reminder_type"]
        if rtype == "monthly":
            send_monthly_reminder(partner_name)
        elif rtype == "quarterly":
            send_quarterly_reminder(partner_name)
        elif rtype == "update":
            send_update_reminder()


def _escape(text: str) -> str:
    """Escape special characters for AppleScript strings."""
    return text.replace("\\", "\\\\").replace('"', '\\"')
