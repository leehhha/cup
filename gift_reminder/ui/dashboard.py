"""Main dashboard UI - the primary screen after setup."""

import customtkinter as ctk
from datetime import date, datetime
from gift_reminder.ui.theme import COLORS, FONTS, LAYOUT
from gift_reminder.ui.components import (
    StyledButton,
    Card,
    SectionTitle,
    SubTitle,
    StyledEntry,
    StyledTextbox,
    StarRating,
)
from gift_reminder.gift_engine import GiftEngine


class Dashboard(ctk.CTkFrame):
    """Main app dashboard showing suggestions, history, and reminders."""

    def __init__(self, master, db, show_update_quiz):
        super().__init__(master, fg_color=COLORS["bg_primary"])
        self.db = db
        self.engine = GiftEngine(db)
        self.show_update_quiz = show_update_quiz

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self._build_header()

        # Scrollable content
        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg_primary"],
            scrollbar_button_color=COLORS["bg_card"],
        )
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=LAYOUT["padding"], pady=(0, LAYOUT["padding"]))
        self.scroll.grid_columnconfigure(0, weight=1)

        self._build_content()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], height=70, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        profile = self.db.get_profile()
        partner_name = profile["partner_name"] if profile else "Your Partner"

        title = ctk.CTkLabel(
            header,
            text=f"\U0001f381  Gifts for {partner_name}",
            font=FONTS["heading"],
            text_color=COLORS["text_primary"],
        )
        title.grid(row=0, column=0, padx=LAYOUT["padding"], pady=15, sticky="w")

        # Check for update quiz due
        due_reminders = self.db.get_due_reminders()
        update_due = any(r["reminder_type"] == "update" for r in due_reminders)
        if update_due:
            update_btn = StyledButton(
                header, text="6-Month Check-In Due!", command=self.show_update_quiz, style="primary", width=200
            )
            update_btn.grid(row=0, column=2, padx=LAYOUT["padding"], pady=15, sticky="e")

    def _build_content(self):
        """Build all dashboard sections."""
        row = 0

        # --- Active Reminders Section ---
        due_reminders = self.db.get_due_reminders()
        gift_reminders = [r for r in due_reminders if r["reminder_type"] in ("monthly", "quarterly")]

        if gift_reminders:
            row = self._build_reminder_alerts(row, gift_reminders)

        # --- Gift Suggestions Section ---
        row = self._build_suggestions_section(row)

        # --- Quick Log Section ---
        row = self._build_log_section(row)

        # --- Gift History Section ---
        row = self._build_history_section(row)

        # --- Upcoming Reminders Section ---
        row = self._build_upcoming_section(row)

    def _build_reminder_alerts(self, row: int, reminders: list) -> int:
        """Show active reminder alerts."""
        for reminder in reminders:
            alert_card = Card(self.scroll)
            alert_card.grid(row=row, column=0, sticky="ew", pady=(0, 10))
            alert_card.grid_columnconfigure(1, weight=1)

            rtype = reminder["reminder_type"]
            if rtype == "monthly":
                icon = "\U0001f490"
                msg = "Monthly Gift Reminder"
                desc = "Time for a small, thoughtful gift! Check the suggestions below."
            else:
                icon = "\u2728"
                msg = "Quarterly Surprise Time!"
                desc = "It's time for a special surprise gift. See ideas below."

            icon_label = ctk.CTkLabel(alert_card, text=icon, font=("Arial", 28))
            icon_label.grid(row=0, column=0, rowspan=2, padx=(16, 8), pady=12)

            title = ctk.CTkLabel(
                alert_card, text=msg, font=FONTS["subheading"], text_color=COLORS["warning"], anchor="w"
            )
            title.grid(row=0, column=1, sticky="w", pady=(12, 0))

            sub = ctk.CTkLabel(
                alert_card, text=desc, font=FONTS["small"], text_color=COLORS["text_secondary"], anchor="w"
            )
            sub.grid(row=1, column=1, sticky="w", pady=(0, 12))

            dismiss_btn = StyledButton(
                alert_card,
                text="Dismiss",
                command=lambda rid=reminder["id"]: self._dismiss_reminder(rid),
                style="ghost",
                width=80,
            )
            dismiss_btn.grid(row=0, column=2, rowspan=2, padx=12)

            row += 1

        return row

    def _build_suggestions_section(self, row: int) -> int:
        """Build gift suggestion cards."""
        # Monthly suggestions
        section_label = SectionTitle(self.scroll, text="Gift Ideas for This Month")
        section_label.grid(row=row, column=0, sticky="w", pady=(16, 4))
        row += 1

        subtitle = SubTitle(self.scroll, text="Personalized picks based on what she loves")
        subtitle.grid(row=row, column=0, sticky="w", pady=(0, 10))
        row += 1

        monthly = self.engine.suggest_monthly_gifts(3)
        for gift in monthly:
            row = self._build_gift_card(row, gift, "monthly")

        # Quarterly suggestions (always show)
        q_label = SectionTitle(self.scroll, text="Surprise Gift Ideas")
        q_label.grid(row=row, column=0, sticky="w", pady=(20, 4))
        row += 1

        q_sub = SubTitle(self.scroll, text="Bigger gestures for quarterly surprises")
        q_sub.grid(row=row, column=0, sticky="w", pady=(0, 10))
        row += 1

        quarterly = self.engine.suggest_quarterly_gifts(3)
        for gift in quarterly:
            row = self._build_gift_card(row, gift, "quarterly")

        # Refresh button
        refresh_btn = StyledButton(
            self.scroll, text="Refresh Suggestions", command=self._refresh, style="secondary", width=200
        )
        refresh_btn.grid(row=row, column=0, pady=(8, 16))
        row += 1

        return row

    def _build_gift_card(self, row: int, gift: dict, gift_type: str) -> int:
        """Build a single gift suggestion card."""
        card = Card(self.scroll)
        card.grid(row=row, column=0, sticky="ew", pady=4)
        card.grid_columnconfigure(1, weight=1)

        # Effort indicator
        effort_map = {1: "\u26a1 Easy", 2: "\U0001f44d Simple"}
        effort_text = effort_map.get(gift["effort"], "\u26a1 Easy")

        effort_label = ctk.CTkLabel(
            card,
            text=effort_text,
            font=FONTS["tiny"],
            text_color=COLORS["success"],
            width=60,
        )
        effort_label.grid(row=0, column=0, padx=(16, 8), pady=12)

        name_label = ctk.CTkLabel(
            card,
            text=gift["name"],
            font=FONTS["body"],
            text_color=COLORS["text_primary"],
            anchor="w",
            wraplength=450,
        )
        name_label.grid(row=0, column=1, sticky="w", padx=4, pady=12)

        # Tags
        tag_text = " \u2022 ".join(gift["tags"][:3])
        tags = ctk.CTkLabel(
            card, text=tag_text, font=FONTS["tiny"], text_color=COLORS["text_muted"], anchor="w"
        )
        tags.grid(row=1, column=1, sticky="w", padx=4, pady=(0, 8))

        log_btn = StyledButton(
            card,
            text="Log as Given",
            command=lambda g=gift: self._log_gift_from_suggestion(g, gift_type),
            style="secondary",
            width=110,
        )
        log_btn.grid(row=0, column=2, rowspan=2, padx=12)

        return row + 1

    def _build_log_section(self, row: int) -> int:
        """Build the quick gift logging section."""
        section_label = SectionTitle(self.scroll, text="Log a Gift")
        section_label.grid(row=row, column=0, sticky="w", pady=(20, 4))
        row += 1

        subtitle = SubTitle(self.scroll, text="Record a gift you gave (from suggestions or your own idea)")
        subtitle.grid(row=row, column=0, sticky="w", pady=(0, 10))
        row += 1

        log_card = Card(self.scroll)
        log_card.grid(row=row, column=0, sticky="ew", pady=4)
        log_card.grid_columnconfigure(1, weight=1)

        # Gift name input
        name_label = ctk.CTkLabel(
            log_card, text="Gift:", font=FONTS["body_bold"], text_color=COLORS["text_primary"]
        )
        name_label.grid(row=0, column=0, padx=(16, 8), pady=(16, 4), sticky="w")

        self.log_name_entry = StyledEntry(log_card, placeholder="What did you give?", width=500)
        self.log_name_entry.grid(row=0, column=1, padx=(0, 16), pady=(16, 4), sticky="ew")

        # Type selector
        type_label = ctk.CTkLabel(
            log_card, text="Type:", font=FONTS["body_bold"], text_color=COLORS["text_primary"]
        )
        type_label.grid(row=1, column=0, padx=(16, 8), pady=4, sticky="w")

        self.log_type_var = ctk.StringVar(value="monthly")
        type_frame = ctk.CTkFrame(log_card, fg_color="transparent")
        type_frame.grid(row=1, column=1, sticky="w", pady=4)

        monthly_rb = ctk.CTkRadioButton(
            type_frame,
            text="Monthly",
            variable=self.log_type_var,
            value="monthly",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
            fg_color=COLORS["accent"],
        )
        monthly_rb.grid(row=0, column=0, padx=(0, 20))

        quarterly_rb = ctk.CTkRadioButton(
            type_frame,
            text="Quarterly",
            variable=self.log_type_var,
            value="quarterly",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
            fg_color=COLORS["accent"],
        )
        quarterly_rb.grid(row=0, column=1)

        # Rating
        rating_label = ctk.CTkLabel(
            log_card, text="Rating:", font=FONTS["body_bold"], text_color=COLORS["text_primary"]
        )
        rating_label.grid(row=2, column=0, padx=(16, 8), pady=4, sticky="w")

        self.log_rating = StarRating(log_card)
        self.log_rating.grid(row=2, column=1, sticky="w", pady=4)

        # Notes
        notes_label = ctk.CTkLabel(
            log_card, text="Notes:", font=FONTS["body_bold"], text_color=COLORS["text_primary"]
        )
        notes_label.grid(row=3, column=0, padx=(16, 8), pady=4, sticky="nw")

        self.log_notes = StyledTextbox(log_card, height=60, width=500)
        self.log_notes.grid(row=3, column=1, padx=(0, 16), pady=4, sticky="ew")

        save_btn = StyledButton(log_card, text="Save Gift", command=self._save_manual_gift, width=120)
        save_btn.grid(row=4, column=1, sticky="e", padx=16, pady=(8, 16))

        return row + 1

    def _build_history_section(self, row: int) -> int:
        """Build the gift history section."""
        section_label = SectionTitle(self.scroll, text="Gift History")
        section_label.grid(row=row, column=0, sticky="w", pady=(20, 4))
        row += 1

        gifts = self.db.get_recent_gifts(10)
        if not gifts:
            empty = ctk.CTkLabel(
                self.scroll,
                text="No gifts logged yet. Start by giving a gift from the suggestions above!",
                font=FONTS["body"],
                text_color=COLORS["text_muted"],
            )
            empty.grid(row=row, column=0, sticky="w", pady=10)
            return row + 1

        for gift in gifts:
            card = Card(self.scroll)
            card.grid(row=row, column=0, sticky="ew", pady=3)
            card.grid_columnconfigure(1, weight=1)

            # Date
            try:
                d = datetime.fromisoformat(gift["date_given"])
                date_str = d.strftime("%b %d")
            except (ValueError, TypeError):
                date_str = gift["date_given"][:10] if gift["date_given"] else "?"

            date_label = ctk.CTkLabel(
                card, text=date_str, font=FONTS["small"], text_color=COLORS["accent"], width=60
            )
            date_label.grid(row=0, column=0, padx=(16, 8), pady=10)

            name = ctk.CTkLabel(
                card,
                text=gift["gift_name"],
                font=FONTS["body"],
                text_color=COLORS["text_primary"],
                anchor="w",
            )
            name.grid(row=0, column=1, sticky="w", padx=4, pady=10)

            # Type badge
            badge_color = COLORS["accent"] if gift["gift_type"] == "quarterly" else COLORS["accent_soft"]
            badge = ctk.CTkLabel(
                card,
                text=gift["gift_type"].capitalize(),
                font=FONTS["tiny"],
                text_color=COLORS["text_primary"],
                fg_color=badge_color,
                corner_radius=6,
                width=70,
                height=24,
            )
            badge.grid(row=0, column=2, padx=8, pady=10)

            # Rating stars
            if gift.get("rating"):
                stars_text = "\u2605" * gift["rating"] + "\u2606" * (5 - gift["rating"])
                stars = ctk.CTkLabel(
                    card,
                    text=stars_text,
                    font=("Arial", 14),
                    text_color=COLORS["star_filled"],
                    width=80,
                )
                stars.grid(row=0, column=3, padx=(4, 16), pady=10)

            row += 1

        return row

    def _build_upcoming_section(self, row: int) -> int:
        """Show upcoming reminder schedule."""
        section_label = SectionTitle(self.scroll, text="Upcoming Reminders")
        section_label.grid(row=row, column=0, sticky="w", pady=(20, 10))
        row += 1

        reminders = self.db.get_all_reminders()
        for r in reminders:
            card = Card(self.scroll)
            card.grid(row=row, column=0, sticky="ew", pady=3)
            card.grid_columnconfigure(1, weight=1)

            icons = {"monthly": "\U0001f490", "quarterly": "\u2728", "update": "\U0001f504"}
            labels = {"monthly": "Monthly Gift", "quarterly": "Quarterly Surprise", "update": "6-Month Check-In"}

            icon = ctk.CTkLabel(card, text=icons.get(r["reminder_type"], ""), font=("Arial", 18), width=40)
            icon.grid(row=0, column=0, padx=(16, 4), pady=10)

            name = ctk.CTkLabel(
                card,
                text=labels.get(r["reminder_type"], r["reminder_type"]),
                font=FONTS["body"],
                text_color=COLORS["text_primary"],
                anchor="w",
            )
            name.grid(row=0, column=1, sticky="w", padx=4, pady=10)

            try:
                d = date.fromisoformat(r["next_due"])
                date_str = d.strftime("%B %d, %Y")
                today = date.today()
                days_until = (d - today).days
                if days_until <= 0:
                    status = "Due now!"
                    status_color = COLORS["warning"]
                elif days_until <= 7:
                    status = f"In {days_until} days"
                    status_color = COLORS["accent"]
                else:
                    status = date_str
                    status_color = COLORS["text_muted"]
            except (ValueError, TypeError):
                status = r["next_due"]
                status_color = COLORS["text_muted"]

            date_label = ctk.CTkLabel(
                card, text=status, font=FONTS["small"], text_color=status_color
            )
            date_label.grid(row=0, column=2, padx=16, pady=10)

            row += 1

        return row

    # --- Actions ---

    def _dismiss_reminder(self, reminder_id: int):
        self.db.advance_reminder(reminder_id)
        self._refresh()

    def _log_gift_from_suggestion(self, gift: dict, gift_type: str):
        today = date.today().isoformat()
        category = gift["tags"][0] if gift["tags"] else ""
        self.db.add_gift(gift["name"], gift_type, category, today)
        self._refresh()

    def _save_manual_gift(self):
        name = self.log_name_entry.get().strip()
        if not name:
            return

        gift_type = self.log_type_var.get()
        rating = self.log_rating.get_value()
        notes = self.log_notes.get("1.0", "end-1c").strip()
        today = date.today().isoformat()

        self.db.add_gift(name, gift_type, "", today, notes)
        if rating > 0:
            gifts = self.db.get_recent_gifts(1)
            if gifts:
                self.db.rate_gift(gifts[0]["id"], rating, notes)

        self._refresh()

    def _refresh(self):
        """Rebuild the entire dashboard."""
        for w in self.scroll.winfo_children():
            w.destroy()

        # Rebuild header
        for w in self.winfo_children():
            if w != self.scroll:
                w.destroy()
        self._build_header()
        self._build_content()
