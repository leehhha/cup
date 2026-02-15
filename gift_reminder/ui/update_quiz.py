"""6-month update questionnaire UI."""

import customtkinter as ctk
from gift_reminder.ui.theme import COLORS, FONTS, LAYOUT
from gift_reminder.ui.components import StyledButton, Card, StyledTextbox
from gift_reminder.data.questions import UPDATE_QUESTIONS


class UpdateQuiz(ctk.CTkFrame):
    """5-question update check-in shown every 6 months."""

    def __init__(self, master, db, on_complete):
        super().__init__(master, fg_color=COLORS["bg_primary"])
        self.db = db
        self.on_complete = on_complete
        self.current_index = 0
        self.questions = UPDATE_QUESTIONS
        self.answers = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Progress
        self.progress_frame = ctk.CTkFrame(self, fg_color="transparent", height=50)
        self.progress_frame.grid(row=0, column=0, sticky="ew", padx=LAYOUT["padding"], pady=(LAYOUT["padding"], 0))
        self.progress_frame.grid_columnconfigure(0, weight=1)

        # Content
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=LAYOUT["padding"], pady=10)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Nav
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent", height=60)
        self.nav_frame.grid(row=2, column=0, sticky="ew", padx=LAYOUT["padding"], pady=LAYOUT["padding"])
        self.nav_frame.grid_columnconfigure(1, weight=1)

        self._show_intro()

    def _show_intro(self):
        self._clear_content()

        card = Card(self.content_frame)
        card.grid(row=0, column=0, sticky="nsew", pady=20)
        card.grid_columnconfigure(0, weight=1)

        icon = ctk.CTkLabel(card, text="\U0001f504", font=("Arial", 48))
        icon.grid(row=0, column=0, pady=(40, 10))

        title = ctk.CTkLabel(
            card, text="6-Month Check-In", font=FONTS["heading_large"], text_color=COLORS["text_primary"]
        )
        title.grid(row=1, column=0, pady=(0, 10))

        msg = ctk.CTkLabel(
            card,
            text="Time for a quick update! Just 5 questions\n"
            "to help me give you better gift suggestions.\n\n"
            "This helps keep recommendations fresh and relevant.",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            justify="center",
        )
        msg.grid(row=2, column=0, pady=(0, 30), padx=40)

        start_btn = StyledButton(card, text="Start Check-In", command=self._start, width=200)
        start_btn.grid(row=3, column=0, pady=(0, 40))

    def _start(self):
        self.current_index = 0
        self._show_question()

    def _show_question(self):
        self._clear_content()
        self._update_progress()

        q = self.questions[self.current_index]

        q_num = ctk.CTkLabel(
            self.content_frame,
            text=f"Question {self.current_index + 1} of {len(self.questions)}",
            font=FONTS["small"],
            text_color=COLORS["accent"],
            anchor="w",
        )
        q_num.grid(row=0, column=0, sticky="w", pady=(10, 8))

        question_label = ctk.CTkLabel(
            self.content_frame,
            text=q["text"],
            font=FONTS["subheading"],
            text_color=COLORS["text_primary"],
            anchor="w",
            wraplength=600,
        )
        question_label.grid(row=1, column=0, sticky="w", pady=(0, 20))

        self.answer_widget = StyledTextbox(self.content_frame, height=120, width=600)
        self.answer_widget.grid(row=2, column=0, sticky="w")

        if q["key"] in self.answers:
            self.answer_widget.insert("1.0", self.answers[q["key"]])

        self._update_nav()

    def _update_progress(self):
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

    def _update_nav(self):
        for w in self.nav_frame.winfo_children():
            w.destroy()

        if self.current_index > 0:
            back_btn = StyledButton(self.nav_frame, text="Back", command=self._prev, style="ghost", width=100)
            back_btn.grid(row=0, column=0, sticky="w")

        is_last = self.current_index == len(self.questions) - 1
        next_text = "Complete" if is_last else "Next"
        next_cmd = self._finish if is_last else self._next

        next_btn = StyledButton(self.nav_frame, text=next_text, command=next_cmd, width=140)
        next_btn.grid(row=0, column=2, sticky="e")

    def _save_current(self):
        q = self.questions[self.current_index]
        answer = self.answer_widget.get("1.0", "end-1c").strip()
        if answer:
            self.answers[q["key"]] = answer

    def _next(self):
        self._save_current()
        if self.current_index < len(self.questions) - 1:
            self.current_index += 1
            self._show_question()

    def _prev(self):
        self._save_current()
        if self.current_index > 0:
            self.current_index -= 1
            self._show_question()

    def _finish(self):
        self._save_current()

        for q in self.questions:
            answer = self.answers.get(q["key"], "")
            if answer:
                self.db.save_update_answer(q["text"], answer)

        # Advance the update reminder
        reminders = self.db.get_all_reminders()
        for r in reminders:
            if r["reminder_type"] == "update":
                self.db.advance_reminder(r["id"])
                break

        self.on_complete()

    def _clear_content(self):
        for w in self.content_frame.winfo_children():
            w.destroy()
