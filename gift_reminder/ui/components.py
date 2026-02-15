"""Reusable UI components for consistent styling."""

import customtkinter as ctk
from gift_reminder.ui.theme import COLORS, FONTS, LAYOUT


def configure_app_theme():
    """Set up the global customtkinter theme."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")


class StyledButton(ctk.CTkButton):
    """A styled button with consistent appearance."""

    def __init__(self, master, text, command=None, style="primary", width=None, **kwargs):
        styles = {
            "primary": {
                "fg_color": COLORS["accent"],
                "hover_color": COLORS["accent_hover"],
                "text_color": COLORS["text_primary"],
            },
            "secondary": {
                "fg_color": COLORS["bg_card"],
                "hover_color": COLORS["accent_soft"],
                "text_color": COLORS["text_primary"],
            },
            "ghost": {
                "fg_color": "transparent",
                "hover_color": COLORS["bg_card"],
                "text_color": COLORS["text_secondary"],
            },
        }
        s = styles.get(style, styles["primary"])
        super().__init__(
            master,
            text=text,
            command=command,
            fg_color=s["fg_color"],
            hover_color=s["hover_color"],
            text_color=s["text_color"],
            corner_radius=LAYOUT["corner_radius"],
            height=LAYOUT["button_height"],
            width=width or 160,
            font=FONTS["body_bold"],
            **kwargs,
        )


class Card(ctk.CTkFrame):
    """A styled card container."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["bg_card"],
            corner_radius=LAYOUT["corner_radius"],
            **kwargs,
        )


class SectionTitle(ctk.CTkLabel):
    """A section title label."""

    def __init__(self, master, text, **kwargs):
        super().__init__(
            master,
            text=text,
            font=FONTS["heading"],
            text_color=COLORS["text_primary"],
            anchor="w",
            **kwargs,
        )


class SubTitle(ctk.CTkLabel):
    """A subtitle label."""

    def __init__(self, master, text, **kwargs):
        super().__init__(
            master,
            text=text,
            font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            anchor="w",
            **kwargs,
        )


class StyledEntry(ctk.CTkEntry):
    """A styled text entry field."""

    def __init__(self, master, placeholder="", width=None, **kwargs):
        super().__init__(
            master,
            placeholder_text=placeholder,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_muted"],
            corner_radius=8,
            height=LAYOUT["input_height"],
            width=width or 400,
            font=FONTS["body"],
            **kwargs,
        )


class StyledTextbox(ctk.CTkTextbox):
    """A styled multiline text box."""

    def __init__(self, master, height=80, width=None, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            corner_radius=8,
            height=height,
            width=width or 400,
            font=FONTS["body"],
            border_width=1,
            **kwargs,
        )


class OptionSelector(ctk.CTkFrame):
    """A row of selectable option buttons (single or multi-select)."""

    def __init__(self, master, options: list[str], multi_select=False, columns=3, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.options = options
        self.multi_select = multi_select
        self.selected = set()
        self.buttons = []

        for i, opt in enumerate(options):
            row = i // columns
            col = i % columns
            btn = ctk.CTkButton(
                self,
                text=opt,
                command=lambda o=opt: self._toggle(o),
                fg_color=COLORS["bg_input"],
                hover_color=COLORS["accent_soft"],
                text_color=COLORS["text_secondary"],
                corner_radius=8,
                height=36,
                width=200,
                font=FONTS["small"],
                border_width=1,
                border_color=COLORS["border"],
            )
            btn.grid(row=row, column=col, padx=4, pady=4, sticky="ew")
            self.buttons.append((opt, btn))

        # Make columns expand evenly
        for c in range(columns):
            self.grid_columnconfigure(c, weight=1)

    def _toggle(self, option: str):
        if self.multi_select:
            if option in self.selected:
                self.selected.discard(option)
            else:
                self.selected.add(option)
        else:
            self.selected = {option}

        # Update button visuals
        for opt, btn in self.buttons:
            if opt in self.selected:
                btn.configure(
                    fg_color=COLORS["accent"],
                    text_color=COLORS["text_primary"],
                    border_color=COLORS["accent"],
                )
            else:
                btn.configure(
                    fg_color=COLORS["bg_input"],
                    text_color=COLORS["text_secondary"],
                    border_color=COLORS["border"],
                )

    def get_value(self) -> str:
        if self.multi_select:
            return ", ".join(sorted(self.selected))
        return next(iter(self.selected), "")


class StarRating(ctk.CTkFrame):
    """A 5-star rating widget."""

    def __init__(self, master, initial=0, on_change=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.rating = initial
        self.on_change = on_change
        self.stars = []

        for i in range(5):
            star = ctk.CTkButton(
                self,
                text="\u2605",
                command=lambda idx=i: self._set_rating(idx + 1),
                fg_color="transparent",
                hover_color=COLORS["bg_primary"],
                text_color=COLORS["star_filled"] if i < initial else COLORS["star_empty"],
                width=32,
                height=32,
                font=("Arial", 22),
            )
            star.grid(row=0, column=i, padx=1)
            self.stars.append(star)

    def _set_rating(self, value: int):
        self.rating = value
        for i, star in enumerate(self.stars):
            color = COLORS["star_filled"] if i < value else COLORS["star_empty"]
            star.configure(text_color=color)
        if self.on_change:
            self.on_change(value)

    def get_value(self) -> int:
        return self.rating
