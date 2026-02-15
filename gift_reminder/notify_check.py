"""Standalone script for launchd to check and send notifications.

This runs in the background via macOS launchd and checks for due reminders.
"""

from gift_reminder.database import Database
from gift_reminder.notifications import check_and_notify


def main():
    db = Database()
    try:
        if db.is_setup_complete():
            check_and_notify(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
