"""Occasion generation and timeline logic.

Generates upcoming gift occasions from:
- Recurring monthly gifts (1st of each month)
- Recurring quarterly surprises (every 3 months)
- Special dates (birthday, anniversary, holidays)
"""

from datetime import date, timedelta


def _mothers_day(year: int) -> date:
    """Return the 2nd Sunday in May for a given year."""
    may1 = date(year, 5, 1)
    # day_of_week: Monday=0, Sunday=6
    days_until_sunday = (6 - may1.weekday()) % 7
    first_sunday = may1 + timedelta(days=days_until_sunday)
    return first_sunday + timedelta(weeks=1)


def _next_occurrence_md(month: int, day: int, after: date) -> date:
    """Return the next occurrence of MM/DD on or after `after`."""
    this_year = date(after.year, month, min(day, 28))
    if this_year >= after:
        return this_year
    return date(after.year + 1, month, min(day, 28))


def _parse_md(md_str: str) -> tuple[int, int] | None:
    """Parse 'MM/DD' or 'MM-DD' into (month, day). Returns None on bad input."""
    for sep in ("/", "-"):
        if sep in md_str:
            parts = md_str.strip().split(sep)
            if len(parts) == 2:
                try:
                    return int(parts[0]), int(parts[1])
                except ValueError:
                    return None
    return None


def generate_upcoming_occasions(db, horizon_days: int = 180) -> list[dict]:
    """Ensure occasion rows exist for the next `horizon_days` days.

    Creates any missing occasions and returns all active ones (sorted by date).
    """
    today = date.today()
    horizon = today + timedelta(days=horizon_days)

    # --- Recurring monthly gifts (1st of each month) ---
    d = date(today.year, today.month, 1)
    if d < today:
        m = d.month + 1
        y = d.year
        if m > 12:
            m, y = 1, y + 1
        d = date(y, m, 1)
    while d <= horizon:
        _ensure_occasion(db, "monthly", "Monthly Gift", d.isoformat())
        m = d.month + 1
        y = d.year
        if m > 12:
            m, y = 1, y + 1
        d = date(y, m, 1)

    # --- Recurring quarterly surprises ---
    quarter_starts = []
    for qm in (1, 4, 7, 10):
        qd = date(today.year, qm, 1)
        if qd >= today:
            quarter_starts.append(qd)
        # Next year too
        qd_next = date(today.year + 1, qm, 1)
        if qd_next <= horizon:
            quarter_starts.append(qd_next)
    for qd in quarter_starts:
        if qd <= horizon:
            _ensure_occasion(db, "quarterly", "Quarterly Surprise", qd.isoformat())

    # --- Special dates from DB ---
    special_dates = db.get_special_dates()
    for sd in special_dates:
        name = sd["occasion_name"]
        md = sd["date_md"]

        # Mother's Day is calculated dynamically
        if name == "mothers_day":
            for yr in (today.year, today.year + 1):
                md_date = _mothers_day(yr)
                if today <= md_date <= horizon:
                    _ensure_occasion(db, "holiday", "Mother's Day", md_date.isoformat())
            continue

        parsed = _parse_md(md)
        if not parsed:
            continue
        month, day = parsed

        next_date = _next_occurrence_md(month, day, today)
        if next_date <= horizon:
            label = _label_for_occasion(name)
            _ensure_occasion(db, name, label, next_date.isoformat())

    return db.get_upcoming_occasions(20)


def _ensure_occasion(db, occasion_type: str, label: str, occasion_date: str):
    """Create an occasion row if one doesn't already exist for this type+date."""
    existing = db.find_occasion_by_date_type(occasion_date, occasion_type)
    if not existing:
        db.create_occasion(occasion_type, label, occasion_date)


def _label_for_occasion(name: str) -> str:
    labels = {
        "birthday": "Her Birthday",
        "anniversary": "Anniversary",
        "valentines": "Valentine's Day",
        "christmas": "Christmas",
        "mothers_day": "Mother's Day",
    }
    return labels.get(name, name.replace("_", " ").title())


def build_timeline(db) -> dict:
    """Build the full timeline data structure for the template.

    Returns: {
        "next_up": occasion | None,
        "upcoming": [occasions],
        "past": [occasions],
    }
    """
    today = date.today()

    # Generate/refresh upcoming occasions
    all_upcoming = generate_upcoming_occasions(db)

    # Annotate with days_until and display info
    next_up = None
    upcoming = []
    for occ in all_upcoming:
        occ_date = date.fromisoformat(occ["occasion_date"])
        days = (occ_date - today).days
        occ["days_until"] = days
        occ["date_display"] = occ_date.strftime("%B %-d, %Y")
        occ["icon"] = _icon_for_type(occ["occasion_type"])

        if days < 0:
            occ["days_label"] = "Overdue!"
        elif days == 0:
            occ["days_label"] = "Today!"
        elif days == 1:
            occ["days_label"] = "Tomorrow!"
        else:
            occ["days_label"] = f"in {days} days"

        if occ["state"] in ("upcoming", "planning", "selected", "given"):
            if next_up is None:
                next_up = occ
            else:
                upcoming.append(occ)

    # Past occasions with ratings
    past = db.get_past_occasions(10)
    for occ in past:
        occ["icon"] = _icon_for_type(occ["occasion_type"])
        occ_date = date.fromisoformat(occ["occasion_date"])
        occ["date_display"] = occ_date.strftime("%B %-d, %Y")
        rating = db.get_rating_for_occasion(occ["id"])
        occ["rating"] = rating

    return {"next_up": next_up, "upcoming": upcoming, "past": past}


def _icon_for_type(occasion_type: str) -> str:
    icons = {
        "monthly": "&#128157;",
        "quarterly": "&#127881;",
        "birthday": "&#127874;",
        "anniversary": "&#128141;",
        "valentines": "&#128152;",
        "christmas": "&#127876;",
        "mothers_day": "&#127801;",
    }
    return icons.get(occasion_type, "&#127873;")
