"""Bonus questions UI - lets engaged users answer additional questions after setup."""

import customtkinter as ctk
from gift_reminder.ui.theme import COLORS, FONTS, LAYOUT
from gift_reminder.ui.components import (
    StyledButton,
    Card,
    StyledTextbox,
    OptionSelector,
    StarRating,
)
from gift_reminder.data.questions import BONUS_QUESTIONS


class BonusQuiz(ctk.CTkFrame):
    """Walk the user through unanswered bonus questions to improve suggestions."""

    def __init__(self, master, db, on_complete):
        super().__init__(master, fg_color=COLORS["bg_primary"])
        self.db = db
        self.on_complete = on_complete
        self.current_index = 0
        self.answers = {}

        # Filter to only unanswered bonus questions
        answered_keys = db.get_answered_question_keys()
        self.questions = [q for q in BONUS_QUESTIONS if q["key"] not in answered_keys]

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Progress
        self.progress_frame = ctk.CTkFrame(self, fg_color="transparent", height=60)
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

        if self.questions:
            self._show_intro()
        else:
            self._show_all_done()

    # --- Intro / Outro ---

    def _show_intro(self):
        self._clear_content()

        card = Card(self.content_frame)
        card.grid(row=0, column=0, sticky="nsew", pady=20)
        card.grid_columnconfigure(0, weight=1)

        icon = ctk.CTkLabel(card, text="\U0001f4a1", font=("Arial", 48))
        icon.grid(row=0, column=0, pady=(40, 10))

        title = ctk.CTkLabel(
            card, text="Improve Your Suggestions", font=FONTS["heading_large"], text_color=COLORS["text_primary"]
        )
        title.grid(row=1, column=0, pady=(0, 10))

        count = len(self.questions)
        msg = ctk.CTkLabel(
            card,
            text=f"Answer {count} more question{'s' if count != 1 else ''} to help\n"
            "me suggest even better gifts.\n\n"
            "You can stop anytime and come back later.",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            justify="center",
        )
        msg.grid(row=2, column=0, pady=(0, 30), padx=40)

        start_btn = StyledButton(card, text="Let's Go", command=self._start, width=200)
        start_btn.grid(row=3, column=0, pady=(0, 40))

    def _show_all_done(self):
        self._clear_content()

        card = Card(self.content_frame)
        card.grid(row=0, column=0, sticky="nsew", pady=20)
        card.grid_columnconfigure(0, weight=1)

        icon = ctk.CTkLabel(card, text="\u2705", font=("Arial", 48))
        icon.grid(row=0, column=0, pady=(40, 10))

        title = ctk.CTkLabel(
            card, text="All Caught Up!", font=FONTS["heading_large"], text_color=COLORS["text_primary"]
        )
        title.grid(row=1, column=0, pady=(0, 10))

        msg = ctk.CTkLabel(
            card,
            text="You've answered all available bonus questions.\n"
            "Your gift suggestions are as personalized as possible!",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            justify="center",
        )
        msg.grid(row=2, column=0, pady=(0, 30), padx=40)

        back_btn = StyledButton(card, text="Back to Dashboard", command=self.on_complete, width=200)
        back_btn.grid(row=3, column=0, pady=(0, 40))

    def _show_complete(self):
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

        answered = len(self.answers)
        title = ctk.CTkLabel(
            card, text="Nice Work!", font=FONTS["heading_large"], text_color=COLORS["text_primary"]
        )
        title.grid(row=1, column=0, pady=(0, 10))

        msg = ctk.CTkLabel(
            card,
            text=f"You answered {answered} more question{'s' if answered != 1 else ''}.\n"
            "Your gift suggestions just got better!",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            justify="center",
        )
        msg.grid(row=2, column=0, pady=(0, 30), padx=40)

        back_btn = StyledButton(card, text="Back to Dashboard", command=self.on_complete, width=200)
        back_btn.grid(row=3, column=0, pady=(0, 40))

    # --- Question flow ---

    def _start(self):
        self.current_index = 0
        self._show_question()

    def _show_question(self):
        self._clear_content()
        self._update_progress()

        q = self.questions[self.current_index]
        section = q.get("section", "")

        # Section header
        section_label = ctk.CTkLabel(
            self.content_frame, text=section, font=FONTS["small"], text_color=COLORS["accent"], anchor="w"
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

        # Answer widget (same types as setup wizard)
        if q["type"] == "text":
            self.answer_widget = StyledTextbox(self.content_frame, height=100, width=600)
            self.answer_widget.grid(row=3, column=0, sticky="w")
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

        pct_label = ctk.CTkLabel(
            self.progress_frame,
            text=f"{int(progress * 100)}% complete",
            font=FONTS["tiny"],
            text_color=COLORS["text_muted"],
        )
        pct_label.grid(row=1, column=0, sticky="e")

    def _update_nav(self):
        for w in self.nav_frame.winfo_children():
            w.destroy()

        if self.current_index > 0:
            back_btn = StyledButton(self.nav_frame, text="Back", command=self._prev, style="ghost", width=100)
            back_btn.grid(row=0, column=0, sticky="w")

        # Save & exit button (can leave anytime)
        exit_btn = StyledButton(
            self.nav_frame, text="Save & Exit", command=self._save_and_exit, style="ghost", width=110
        )
        exit_btn.grid(row=0, column=1)

        is_last = self.current_index == len(self.questions) - 1
        next_text = "Finish" if is_last else "Next"
        next_cmd = self._finish if is_last else self._next

        next_btn = StyledButton(self.nav_frame, text=next_text, command=next_cmd, width=140)
        next_btn.grid(row=0, column=2, sticky="e")

    # --- Answer handling ---

    def _get_current_answer(self) -> str:
        if isinstance(self.answer_widget, StyledTextbox):
            return self.answer_widget.get("1.0", "end-1c").strip()
        elif isinstance(self.answer_widget, OptionSelector):
            return self.answer_widget.get_value()
        elif isinstance(self.answer_widget, StarRating):
            return str(self.answer_widget.get_value())
        return ""

    def _save_current_answer(self):
        answer = self._get_current_answer()
        q = self.questions[self.current_index]
        if answer:
            self.answers[q["key"]] = answer

    def _next(self):
        self._save_current_answer()
        if self.current_index < len(self.questions) - 1:
            self.current_index += 1
            self._show_question()

    def _prev(self):
        self._save_current_answer()
        if self.current_index > 0:
            self.current_index -= 1
            self._show_question()

    def _persist_answers(self):
        """Save all collected answers to the database."""
        for q in self.questions:
            answer = self.answers.get(q["key"], "")
            if answer:
                self.db.save_setup_answer(q["key"], q["text"], answer, q["category"])

    def _save_and_exit(self):
        self._save_current_answer()
        self._persist_answers()
        self.on_complete()

    def _finish(self):
        self._save_current_answer()
        self._persist_answers()
        self._show_complete()

    def _clear_content(self):
        for w in self.content_frame.winfo_children():
            w.destroy()
