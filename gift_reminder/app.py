"""Main application entry point for Gift Reminder."""

import customtkinter as ctk
from gift_reminder.database import Database
from gift_reminder.notifications import check_and_notify
from gift_reminder.ui.theme import COLORS, LAYOUT
from gift_reminder.ui.components import configure_app_theme
from gift_reminder.ui.setup_wizard import SetupWizard
from gift_reminder.ui.dashboard import Dashboard
from gift_reminder.ui.update_quiz import UpdateQuiz


class GiftReminderApp(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        configure_app_theme()

        self.title("Gift Reminder")
        self.geometry(f"{LAYOUT['window_width']}x{LAYOUT['window_height']}")
        self.minsize(700, 550)
        self.configure(fg_color=COLORS["bg_primary"])

        # Center window on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (LAYOUT["window_width"] // 2)
        y = (self.winfo_screenheight() // 2) - (LAYOUT["window_height"] // 2)
        self.geometry(f"+{x}+{y}")

        # Database
        self.db = Database()

        # Check for due notifications on startup
        check_and_notify(self.db)

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Show appropriate screen
        if self.db.is_setup_complete():
            self._show_dashboard()
        else:
            self._show_setup()

    def _show_setup(self):
        self._clear_screen()
        wizard = SetupWizard(self, self.db, on_complete=self._show_dashboard)
        wizard.grid(row=0, column=0, sticky="nsew")

    def _show_dashboard(self):
        self._clear_screen()
        dashboard = Dashboard(self, self.db, show_update_quiz=self._show_update_quiz)
        dashboard.grid(row=0, column=0, sticky="nsew")

    def _show_update_quiz(self):
        self._clear_screen()
        quiz = UpdateQuiz(self, self.db, on_complete=self._show_dashboard)
        quiz.grid(row=0, column=0, sticky="nsew")

    def _clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    def on_closing(self):
        self.db.close()
        self.destroy()


def main():
    app = GiftReminderApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
