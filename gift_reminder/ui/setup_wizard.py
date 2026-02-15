"""Setup wizard - walks user through initial 25 questions about their partner."""

import customtkinter as ctk
from gift_reminder.ui.theme import COLORS, FONTS, LAYOUT
from gift_reminder.ui.components import (
    StyledButton,
    Card,
    SectionTitle,
    SubTitle,
    StyledEntry,
    StyledTextbox,
    OptionSelector,
    StarRating,
)
from gift_reminder.data.questions import SETUP_QUESTIONS


class SetupWizard(ctk.CTkFrame):
    """Multi-step setup wizard with one question per screen."""

    def __init__(self, master, db, on_complete):
        super().__init__(master, fg_color=COLORS["bg_primary"])
        self.db = db
        self.on_complete = on_complete
        self.current_index = 0
        self.questions = SETUP_QUESTIONS
        self.answers = {}

        # Main layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Progress bar area
        self.progress_frame = ctk.CTkFrame(self, fg_color="transparent", height=60)
        self.progress_frame.grid(row=0, column=0, sticky="ew", padx=LAYOUT["padding"], pady=(LAYOUT["padding"], 0))
        self.progress_frame.grid_columnconfigure(0, weight=1)

        # Content area
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=LAYOUT["padding"], pady=10)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Navigation area
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent", height=60)
        self.nav_frame.grid(row=2, column=0, sticky="ew", padx=LAYOUT["padding"], pady=LAYOUT["padding"])
        self.nav_frame.grid_columnconfigure(1, weight=1)

        self._show_welcome()

    def _show_welcome(self):
        """Show the welcome screen before questions begin."""
        self._clear_content()

        # Welcome message
        welcome_card = Card(self.content_frame)
        welcome_card.grid(row=0, column=0, sticky="nsew", pady=20)
        welcome_card.grid_columnconfigure(0, weight=1)

        icon_label = ctk.CTkLabel(
            welcome_card, text="\U0001f381", font=("Arial", 64), text_color=COLORS["text_primary"]
        )
        icon_label.grid(row=0, column=0, pady=(40, 10))

        title = ctk.CTkLabel(
            welcome_card,
            text="Gift Reminder",
            font=FONTS["heading_large"],
            text_color=COLORS["text_primary"],
        )
        title.grid(row=1, column=0, pady=(0, 10))

        subtitle = ctk.CTkLabel(
            welcome_card,
            text="Let's set up your personalized gift assistant.\n\n"
            "I'll ask you 25 quick questions about your wife\n"
            "to help suggest thoughtful gifts throughout the year.\n\n"
            "This should only take a few minutes.",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            justify="center",
        )
        subtitle.grid(row=2, column=0, pady=(0, 30), padx=40)

        start_btn = StyledButton(
            welcome_card, text="Let's Get Started", command=self._start_questions, width=220
        )
        start_btn.grid(row=3, column=0, pady=(0, 40))

    def _start_questions(self):
        self.current_index = 0
        self._show_question()

    def _show_question(self):
        """Display the current question."""
        self._clear_content()
        self._update_progress()

        q = self.questions[self.current_index]
        section = q.get("section", "")

        # Section header
        section_label = ctk.CTkLabel(
            self.content_frame,
            text=section,
            font=FONTS["small"],
            text_color=COLORS["accent"],
            anchor="w",
        )
        section_label.grid(row=0, column=0, sticky="w", pady=(10, 2))

        # Question number
        q_num = ctk.CTkLabel(
            self.content_frame,
            text=f"Question {self.current_index + 1} of {len(self.questions)}",
            font=FONTS["tiny"],
            text_color=COLORS["text_muted"],
            anchor="w",
        )
        q_num.grid(row=1, column=0, sticky="w", pady=(0, 8))

        # Question text
        question_label = ctk.CTkLabel(
            self.content_frame,
            text=q["text"],
            font=FONTS["subheading"],
            text_color=COLORS["text_primary"],
            anchor="w",
            wraplength=600,
        )
        question_label.grid(row=2, column=0, sticky="w", pady=(0, 20))

        # Answer widget
        if q["type"] == "text":
            self.answer_widget = StyledTextbox(self.content_frame, height=100, width=600)
            self.answer_widget.grid(row=3, column=0, sticky="w")
            # Restore previous answer if going back
            if q["key"] in self.answers:
                self.answer_widget.insert("1.0", self.answers[q["key"]])

        elif q["type"] == "options":
            self.answer_widget = OptionSelector(
                self.content_frame, options=q["options"], multi_select=False, columns=2
            )
            self.answer_widget.grid(row=3, column=0, sticky="ew")
            if q["key"] in self.answers:
                self.answer_widget._toggle(self.answers[q["key"]])

        elif q["type"] == "multi":
            cols = 3 if len(q["options"]) > 6 else 2
            self.answer_widget = OptionSelector(
                self.content_frame, options=q["options"], multi_select=True, columns=cols
            )
            self.answer_widget.grid(row=3, column=0, sticky="ew")
            if q["key"] in self.answers:
                for val in self.answers[q["key"]].split(", "):
                    if val in q["options"]:
                        self.answer_widget._toggle(val)

        elif q["type"] == "scale":
            scale_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            scale_frame.grid(row=3, column=0, sticky="w")

            low_label = ctk.CTkLabel(
                scale_frame, text="Not very important", font=FONTS["small"], text_color=COLORS["text_muted"]
            )
            low_label.grid(row=0, column=0, padx=(0, 10))

            initial = int(self.answers.get(q["key"], "0"))
            self.answer_widget = StarRating(scale_frame, initial=initial)
            self.answer_widget.grid(row=0, column=1, padx=10)

            high_label = ctk.CTkLabel(
                scale_frame, text="Extremely important", font=FONTS["small"], text_color=COLORS["text_muted"]
            )
            high_label.grid(row=0, column=2, padx=(10, 0))

        # Navigation buttons
        self._update_nav()

    def _update_progress(self):
        """Update the progress bar."""
        for w in self.progress_frame.winfo_children():
            w.destroy()

        progress = (self.current_index + 1) / len(self.questions)
        bar = ctk.CTkProgressBar(
            self.progress_frame,
            progress_color=COLORS["accent"],
            fg_color=COLORS["bg_secondary"],
            height=6,
            corner_radius=3,
        )
        bar.grid(row=0, column=0, sticky="ew", pady=(10, 5))
        bar.set(progress)

        pct_label = ctk.CTkLabel(
            self.progress_frame,
            text=f"{int(progress * 100)}% complete",
            font=FONTS["tiny"],
            text_color=COLORS["text_muted"],
        )
        pct_label.grid(row=1, column=0, sticky="e")

    def _update_nav(self):
        """Update navigation buttons."""
        for w in self.nav_frame.winfo_children():
            w.destroy()

        if self.current_index > 0:
            back_btn = StyledButton(
                self.nav_frame, text="Back", command=self._prev_question, style="ghost", width=100
            )
            back_btn.grid(row=0, column=0, sticky="w")

        is_last = self.current_index == len(self.questions) - 1
        next_text = "Finish Setup" if is_last else "Next"
        next_cmd = self._finish if is_last else self._next_question

        next_btn = StyledButton(
            self.nav_frame, text=next_text, command=next_cmd, width=140
        )
        next_btn.grid(row=0, column=2, sticky="e")

    def _get_current_answer(self) -> str:
        """Extract the answer from the current widget."""
        if isinstance(self.answer_widget, StyledTextbox):
            return self.answer_widget.get("1.0", "end-1c").strip()
        elif isinstance(self.answer_widget, OptionSelector):
            return self.answer_widget.get_value()
        elif isinstance(self.answer_widget, StarRating):
            return str(self.answer_widget.get_value())
        return ""

    def _save_current_answer(self):
        """Save the current answer to memory and optionally skip if empty."""
        answer = self._get_current_answer()
        q = self.questions[self.current_index]
        if answer:
            self.answers[q["key"]] = answer

    def _next_question(self):
        self._save_current_answer()
        if self.current_index < len(self.questions) - 1:
            self.current_index += 1
            self._show_question()

    def _prev_question(self):
        self._save_current_answer()
        if self.current_index > 0:
            self.current_index -= 1
            self._show_question()

    def _finish(self):
        """Save all answers to the database and complete setup."""
        self._save_current_answer()

        # Save profile
        partner_name = self.answers.get("partner_name", "Your Partner")
        self.db.save_profile(partner_name)

        # Save all answers
        for q in self.questions:
            answer = self.answers.get(q["key"], "")
            if answer:
                self.db.save_setup_answer(q["key"], q["text"], answer, q["category"])

        # Initialize reminders
        self.db.init_reminders()

        # Show completion screen
        self._show_complete(partner_name)

    def _show_complete(self, partner_name: str):
        """Show setup completion screen."""
        self._clear_content()
        for w in self.progress_frame.winfo_children():
            w.destroy()
        for w in self.nav_frame.winfo_children():
            w.destroy()

        card = Card(self.content_frame)
        card.grid(row=0, column=0, sticky="nsew", pady=20)
        card.grid_columnconfigure(0, weight=1)

        icon = ctk.CTkLabel(card, text="\u2728", font=("Arial", 48))
        icon.grid(row=0, column=0, pady=(40, 10))

        title = ctk.CTkLabel(
            card,
            text="You're All Set!",
            font=FONTS["heading_large"],
            text_color=COLORS["text_primary"],
        )
        title.grid(row=1, column=0, pady=(0, 10))

        msg = ctk.CTkLabel(
            card,
            text=f"Great! I now have a good understanding of what\n"
            f"{partner_name} would love. Here's what happens next:\n\n"
            f"\u2022  Monthly reminders for small, thoughtful gifts\n"
            f"\u2022  Quarterly surprise gift suggestions\n"
            f"\u2022  Check-ins every 6 months to keep improving\n\n"
            f"Head to your dashboard to see your first suggestions!",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            justify="center",
        )
        msg.grid(row=2, column=0, pady=(0, 30), padx=40)

        go_btn = StyledButton(
            card, text="Go to Dashboard", command=self.on_complete, width=200
        )
        go_btn.grid(row=3, column=0, pady=(0, 40))

    def _clear_content(self):
        for w in self.content_frame.winfo_children():
            w.destroy()
