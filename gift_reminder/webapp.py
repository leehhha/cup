"""Flask web application for Gift Reminder — Timeline-Centric Design."""

import json
import os
import secrets
from datetime import date, datetime
from urllib.parse import quote_plus

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for

from gift_reminder.data.questions import BONUS_QUESTIONS, CHECKIN_3_QUESTIONS, SETUP_QUESTIONS, UPDATE_QUESTIONS
from gift_reminder.database import Database
from gift_reminder.gift_engine import GiftEngine
from gift_reminder.occasions import build_carousel_data, build_timeline, occasion_to_json


COMMON_MILESTONES = [
    {"id": "wedding-anniversary", "emoji": "\U0001f48d", "label": "Wedding Anniversary"},
    {"id": "dating-anniversary", "emoji": "\u2764\ufe0f", "label": "Dating Anniversary"},
    {"id": "day-we-met", "emoji": "\U0001f495", "label": "Day We Met"},
    {"id": "first-date", "emoji": "\U0001f339", "label": "First Date"},
    {"id": "got-engaged", "emoji": "\U0001f48e", "label": "Got Engaged"},
    {"id": "moved-in", "emoji": "\U0001f3e0", "label": "Moved In Together"},
    {"id": "first-i-love-you", "emoji": "\U0001f497", "label": 'First "I Love You"'},
]


def create_app(db_path=None):
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "static"),
    )
    app.secret_key = secrets.token_hex(16)

    db = Database(db_path)
    engine = GiftEngine(db)

    # ------------------------------------------------------------------
    # Root → Timeline
    # ------------------------------------------------------------------
    @app.route("/")
    def index():
        if db.is_setup_complete():
            return redirect(url_for("timeline"))
        return render_template("welcome.html")

    # ------------------------------------------------------------------
    # Setup wizard
    # ------------------------------------------------------------------
    @app.route("/setup/<int:index>", methods=["GET", "POST"])
    def setup_question(index):
        total = len(SETUP_QUESTIONS)
        if index < 0 or index >= total:
            return redirect(url_for("index"))

        question = SETUP_QUESTIONS[index]
        answers = session.get("setup_answers", {})

        # Special dates question uses its own template
        if question.get("type") == "custom_dates":
            if request.method == "POST":
                # Process preset dates and custom dates
                _process_custom_dates_form(db, request.form)
                answers[question["key"]] = request.form.get("answer", "") or "skipped"
                session["setup_answers"] = answers
                if index == total - 1:
                    return _finish_setup(db, answers)
                return redirect(url_for("setup_question", index=index + 1))

            emoji_choices = _emoji_choices()
            return render_template(
                "setup_special_dates.html",
                question=question,
                index=index,
                total=total,
                presets=question.get("preset_dates", []),
                emoji_choices=emoji_choices,
            )

        if request.method == "POST":
            answer = request.form.get("answer", "").strip()
            if answer:
                answers[question["key"]] = answer
                session["setup_answers"] = answers

            if index == total - 1:
                return _finish_setup(db, answers)

            return redirect(url_for("setup_question", index=index + 1))

        current_answer = answers.get(question["key"], "")
        selected_list = [s.strip() for s in current_answer.split(",")] if current_answer else []

        return render_template(
            "setup_question.html",
            question=question,
            index=index,
            total=total,
            current_answer=current_answer,
            selected_list=selected_list,
        )

    # ------------------------------------------------------------------
    # Timeline (new home screen)
    # ------------------------------------------------------------------
    @app.route("/timeline", endpoint="timeline")
    @app.route("/dashboard", endpoint="dashboard")
    def timeline():
        if not db.is_setup_complete():
            return redirect(url_for("index"))

        profile = db.get_profile()
        partner_name = profile["partner_name"]

        carousel = build_carousel_data(db)
        cards_json = json.dumps([occasion_to_json(c) for c in carousel["cards"]])
        next_up_index = carousel["next_up_index"]

        answered_keys = db.get_answered_question_keys()
        bonus_remaining = len([q for q in BONUS_QUESTIONS if q["key"] not in answered_keys])

        # Build to-do items from carousel cards
        todo_items = _build_todo_items(carousel["cards"])

        return render_template(
            "timeline.html",
            partner_name=partner_name,
            cards_json=cards_json,
            next_up_index=next_up_index,
            quick_list=carousel["quick_list"],
            bonus_remaining=bonus_remaining,
            todo_items=todo_items,
        )

    # ------------------------------------------------------------------
    # To-do: mark done via AJAX
    # ------------------------------------------------------------------
    @app.route("/todo/<int:occ_id>/mark-done", methods=["POST"])
    def todo_mark_done(occ_id):
        """Mark an occasion as 'given' from the to-do checklist."""
        occ = db.get_occasion(occ_id)
        if occ and occ["state"] in ("upcoming", "planning", "selected"):
            db.update_occasion_state(occ_id, "given")
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify(ok=True)
        elif request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(ok=False), 400
        return redirect(url_for("timeline"))

    # ------------------------------------------------------------------
    # Occasion state machine
    # ------------------------------------------------------------------
    @app.route("/occasion/<int:occ_id>/give-gift", methods=["POST"])
    def occasion_give_gift(occ_id):
        """Transition: upcoming → planning, then redirect to card selection."""
        occ = db.get_occasion(occ_id)
        if not occ or occ["state"] not in ("upcoming", "planning"):
            return redirect(url_for("timeline"))
        db.update_occasion_state(occ_id, "planning")
        return redirect(url_for("occasion_select_gift", occ_id=occ_id))

    @app.route("/occasion/<int:occ_id>/select-gift")
    def occasion_select_gift(occ_id):
        """Show card-based gift selection UI for this occasion."""
        occ = db.get_occasion(occ_id)
        if not occ or occ["state"] not in ("planning", "selected"):
            return redirect(url_for("timeline"))

        profile = db.get_profile()
        partner_name = profile["partner_name"]

        # Determine gift pool based on occasion type
        otype = occ["occasion_type"]
        if otype == "quarterly":
            gifts = engine.suggest_quarterly_gifts(12)
            pool_type = "quarterly"
        else:
            # monthly, birthday, anniversary, holidays all use monthly pool
            gifts = engine.suggest_monthly_gifts(12)
            pool_type = "monthly"

        card_deck = _build_card_deck(gifts, pool_type)
        card_deck_json = json.dumps(card_deck)

        return render_template(
            "select_gift.html",
            occasion=occ,
            partner_name=partner_name,
            card_deck_json=card_deck_json,
        )

    @app.route("/occasion/<int:occ_id>/confirm-gift", methods=["POST"])
    def occasion_confirm_gift(occ_id):
        """Save selected gift, transition to 'selected' state."""
        occ = db.get_occasion(occ_id)
        if not occ:
            return redirect(url_for("timeline"))

        data = request.get_json(silent=True) or {}
        gift_name = data.get("name", "").strip()
        purchase_link = data.get("purchase_link", "").strip()

        if not gift_name:
            return jsonify(ok=False, error="No gift name"), 400

        db.update_occasion_state(
            occ_id, "selected",
            gift_selected=gift_name,
            gift_purchase_link=purchase_link,
        )
        db.log_interaction(gift_name, "picked", occ["occasion_type"])
        return jsonify(ok=True)

    @app.route("/occasion/<int:occ_id>/mark-given", methods=["POST"])
    def occasion_mark_given(occ_id):
        """Transition: selected → given."""
        occ = db.get_occasion(occ_id)
        if not occ or occ["state"] != "selected":
            return redirect(url_for("timeline"))

        db.update_occasion_state(occ_id, "given")

        # Also log to gift history for the engine
        gift_name = occ.get("gift_selected", "")
        if gift_name:
            otype = occ["occasion_type"]
            gtype = "quarterly" if otype == "quarterly" else "monthly"
            db.add_gift(gift_name, gtype, "", occ["occasion_date"])

        flash("Gift marked as given!", "success")
        return redirect(url_for("timeline"))

    @app.route("/occasion/<int:occ_id>/skip", methods=["POST"])
    def occasion_skip(occ_id):
        """Transition: upcoming → skipped."""
        occ = db.get_occasion(occ_id)
        if not occ or occ["state"] not in ("upcoming", "planning"):
            return redirect(url_for("timeline"))
        db.update_occasion_state(occ_id, "skipped")
        return redirect(url_for("timeline"))

    @app.route("/occasion/<int:occ_id>/change-gift", methods=["POST"])
    def occasion_change_gift(occ_id):
        """Go back to planning from selected state."""
        occ = db.get_occasion(occ_id)
        if not occ or occ["state"] != "selected":
            return redirect(url_for("timeline"))
        db.update_occasion_state(occ_id, "planning", gift_selected="", gift_purchase_link="")
        return redirect(url_for("occasion_select_gift", occ_id=occ_id))

    @app.route("/api/occasion/<int:occ_id>/more-cards", methods=["POST"])
    def occasion_more_cards(occ_id):
        """Return a fresh batch of gift card suggestions (JSON)."""
        occ = db.get_occasion(occ_id)
        if not occ:
            return jsonify(cards=[])

        otype = occ["occasion_type"]
        if otype == "quarterly":
            gifts = engine.suggest_quarterly_gifts(8)
        else:
            gifts = engine.suggest_monthly_gifts(8)

        deck = _build_card_deck(gifts, "quarterly" if otype == "quarterly" else "monthly")
        return jsonify(cards=deck)

    # ------------------------------------------------------------------
    # Rating / Feedback
    # ------------------------------------------------------------------
    @app.route("/occasion/<int:occ_id>/rate", methods=["GET", "POST"])
    def occasion_rate(occ_id):
        """Rate a gift after giving it."""
        occ = db.get_occasion(occ_id)
        if not occ or occ["state"] != "given":
            return redirect(url_for("timeline"))

        if request.method == "POST":
            rating = int(request.form.get("rating", "3"))
            feedback = request.form.get("feedback", "").strip()

            db.save_gift_rating(
                occasion_id=occ_id,
                gift_name=occ.get("gift_selected", ""),
                rating=rating,
                feedback_text=feedback,
                date_given=occ["occasion_date"],
            )
            db.update_occasion_state(occ_id, "complete")

            # Also update gift_history rating if exists
            gifts = db.get_all_gifts()
            for g in gifts:
                if g["gift_name"] == occ.get("gift_selected") and not g.get("rating"):
                    db.rate_gift(g["id"], rating, feedback)
                    break

            flash("Thanks for the feedback!", "success")
            return redirect(url_for("timeline"))

        return render_template("rate_gift.html", occasion=occ)

    # ------------------------------------------------------------------
    # Gift actions (legacy + API)
    # ------------------------------------------------------------------
    @app.route("/log-gift", methods=["POST"])
    def log_gift():
        name = request.form.get("gift_name", "").strip()
        gift_type = request.form.get("gift_type", "monthly")
        rating = request.form.get("rating", "0")
        notes = request.form.get("notes", "").strip()

        if not name:
            flash("Please enter a gift name.", "error")
            return redirect(url_for("timeline"))

        today = date.today().isoformat()
        db.add_gift(name, gift_type, "", today, notes)

        try:
            rating_int = int(rating)
        except ValueError:
            rating_int = 0

        if rating_int > 0:
            gifts = db.get_recent_gifts(1)
            if gifts:
                db.rate_gift(gifts[0]["id"], rating_int, notes)

        flash("Gift logged!", "success")
        return redirect(url_for("timeline"))

    @app.route("/api/log-suggestion", methods=["POST"])
    def api_log_suggestion():
        data = request.get_json(silent=True) or {}
        name = data.get("name", "").strip()
        gift_type = data.get("gift_type", "monthly")
        if not name:
            return jsonify(ok=False, error="Missing gift name"), 400
        today = date.today().isoformat()
        db.add_gift(name, gift_type, "", today)
        return jsonify(ok=True)

    @app.route("/api/log-interaction", methods=["POST"])
    def api_log_interaction():
        data = request.get_json(silent=True) or {}
        gift_name = data.get("name", "").strip()
        action = data.get("action", "").strip()
        gift_type = data.get("gift_type", "")
        if not gift_name or action not in ("picked", "skipped", "link_click"):
            return jsonify(ok=False, error="Invalid interaction"), 400
        db.log_interaction(gift_name, action, gift_type)
        return jsonify(ok=True)

    # ------------------------------------------------------------------
    # Bonus questions
    # ------------------------------------------------------------------
    @app.route("/bonus")
    def bonus_intro():
        answered_keys = db.get_answered_question_keys()
        unanswered = [q for q in BONUS_QUESTIONS if q["key"] not in answered_keys]
        if not unanswered:
            flash("You've answered all bonus questions!", "success")
            return redirect(url_for("timeline"))
        return render_template("bonus_intro.html", total=len(unanswered))

    @app.route("/bonus/<int:index>", methods=["GET", "POST"])
    def bonus_question(index):
        answered_keys = db.get_answered_question_keys()
        unanswered = [q for q in BONUS_QUESTIONS if q["key"] not in answered_keys]
        total = len(unanswered)

        if total == 0:
            return redirect(url_for("timeline"))
        if index < 0 or index >= total:
            return redirect(url_for("bonus_intro"))

        question = unanswered[index]
        answers = session.get("bonus_answers", {})

        if request.method == "POST":
            answer = request.form.get("answer", "").strip()
            if answer:
                answers[question["key"]] = answer
                session["bonus_answers"] = answers

            if index == total - 1:
                return _finish_bonus(db, unanswered, answers)

            return redirect(url_for("bonus_question", index=index + 1))

        current_answer = answers.get(question["key"], "")
        selected_list = [s.strip() for s in current_answer.split(",")] if current_answer else []

        return render_template(
            "bonus_question.html",
            question=question,
            index=index,
            total=total,
            current_answer=current_answer,
            selected_list=selected_list,
        )

    @app.route("/bonus/save-exit")
    def bonus_save_exit():
        answers = session.get("bonus_answers", {})
        answered_keys = db.get_answered_question_keys()
        unanswered = [q for q in BONUS_QUESTIONS if q["key"] not in answered_keys]
        _persist_bonus_answers(db, unanswered, answers)
        session.pop("bonus_answers", None)
        count = len(answers)
        if count:
            flash(f"Saved {count} answer{'s' if count != 1 else ''}!", "success")
        return redirect(url_for("timeline"))

    # ------------------------------------------------------------------
    # 6-month update
    # ------------------------------------------------------------------
    @app.route("/update")
    def update_intro():
        return render_template("update_intro.html")

    @app.route("/update/<int:index>", methods=["GET", "POST"])
    def update_question(index):
        total = len(UPDATE_QUESTIONS)
        if index < 0 or index >= total:
            return redirect(url_for("update_intro"))

        question = UPDATE_QUESTIONS[index]
        answers = session.get("update_answers", {})

        if request.method == "POST":
            answer = request.form.get("answer", "").strip()
            if answer:
                answers[question["key"]] = answer
                session["update_answers"] = answers

            if index == total - 1:
                return _finish_update(db, answers)

            return redirect(url_for("update_question", index=index + 1))

        current_answer = answers.get(question["key"], "")
        return render_template(
            "update_question.html",
            question=question,
            index=index,
            total=total,
            current_answer=current_answer,
        )

    @app.route("/update/complete")
    def update_complete():
        return render_template("update_complete.html")

    # ------------------------------------------------------------------
    # 3-month check-in
    # ------------------------------------------------------------------
    @app.route("/checkin3")
    def checkin3_intro():
        return render_template("checkin3_intro.html")

    @app.route("/checkin3/<int:index>", methods=["GET", "POST"])
    def checkin3_question(index):
        total = len(CHECKIN_3_QUESTIONS)
        if index < 0 or index >= total:
            return redirect(url_for("checkin3_intro"))

        question = CHECKIN_3_QUESTIONS[index]
        answers = session.get("checkin3_answers", {})

        if request.method == "POST":
            answer = request.form.get("answer", "").strip()
            if answer:
                answers[question["key"]] = answer
                session["checkin3_answers"] = answers

            if index == total - 1:
                return _finish_checkin3(db, answers)

            return redirect(url_for("checkin3_question", index=index + 1))

        current_answer = answers.get(question["key"], "")
        selected_list = [s.strip() for s in current_answer.split(",")] if current_answer else []

        return render_template(
            "setup_question.html",
            question=question,
            index=index,
            total=total,
            current_answer=current_answer,
            selected_list=selected_list,
        )

    @app.route("/checkin3/complete")
    def checkin3_complete():
        return render_template("checkin3_complete.html")

    # ------------------------------------------------------------------
    # Settings: Special Dates (structured milestone experience)
    # ------------------------------------------------------------------
    @app.route("/settings/special-dates")
    def settings_dates():
        if not db.is_setup_complete():
            return redirect(url_for("index"))

        all_dates = db.get_all_special_dates()
        today = date.today()

        # Build a lookup of existing common milestones by label
        saved_common = {}
        custom_dates = []
        for d in all_dates:
            # Build display date
            parsed = _parse_date_md(d["date_md"])
            if parsed:
                m, dy = parsed
                if d.get("original_year"):
                    d["display_date"] = date(d["original_year"], m, min(dy, 28)).strftime("%B %-d, %Y")
                    d["full_date"] = date(d["original_year"], m, min(dy, 28)).isoformat()
                else:
                    d["display_date"] = date(today.year, m, min(dy, 28)).strftime("%B %-d")
                    d["full_date"] = ""
            else:
                d["display_date"] = d["date_md"]
                d["full_date"] = ""
            # Anniversary text
            d["anniversary_text"] = ""
            if d.get("original_year") and d.get("recurring"):
                years = today.year - d["original_year"]
                if years > 0:
                    d["anniversary_text"] = f"{years} year{'s' if years != 1 else ''}"

            # Check if this matches a common milestone by name
            matched = False
            for ms in COMMON_MILESTONES:
                if d["occasion_name"].lower().replace(" ", "") == ms["label"].lower().replace(" ", ""):
                    saved_common[ms["id"]] = d
                    matched = True
                    break
            if not matched:
                # Not a system-level date (birthday, anniversary, valentines, etc.)
                if d.get("is_custom"):
                    custom_dates.append(d)

        return render_template(
            "settings_dates.html",
            milestones=COMMON_MILESTONES,
            saved_common=saved_common,
            custom_dates=custom_dates,
            emoji_choices=_emoji_choices(),
        )

    @app.route("/settings/special-dates/save", methods=["POST"])
    def settings_dates_save():
        """Bulk save common milestones from checkboxes."""
        if not db.is_setup_complete():
            return redirect(url_for("index"))

        checked_ids = request.form.getlist("milestone_checked")

        for ms in COMMON_MILESTONES:
            date_val = request.form.get(f"milestone_date_{ms['id']}", "").strip()
            if ms["id"] in checked_ids and date_val:
                try:
                    d = date.fromisoformat(date_val)
                    date_md = f"{d.month:02d}/{d.day:02d}"
                    db.save_special_date(
                        ms["label"], date_md, enabled=True,
                        emoji=ms["emoji"], original_year=d.year,
                        is_custom=True, recurring=True,
                    )
                except ValueError:
                    continue
            elif ms["id"] not in checked_ids:
                # If unchecked, remove it if it exists
                existing = db.get_all_special_dates()
                for ex in existing:
                    if ex["occasion_name"].lower().replace(" ", "") == ms["label"].lower().replace(" ", ""):
                        db.delete_special_date(ex["id"])
                        break

        flash("Special dates saved!", "success")
        return redirect(url_for("settings_dates"))

    @app.route("/settings/special-dates/custom/add", methods=["POST"])
    def settings_date_custom_add():
        if not db.is_setup_complete():
            return redirect(url_for("index"))

        name = request.form.get("name", "").strip()[:50]
        date_val = request.form.get("date_val", "").strip()
        emoji = request.form.get("emoji", "\u2764\ufe0f").strip()
        recurring = request.form.get("recurring", "1") == "1"

        if not name or not date_val:
            flash("Name and date are required.", "error")
            return redirect(url_for("settings_dates"))

        try:
            d = date.fromisoformat(date_val)
            date_md = f"{d.month:02d}/{d.day:02d}"
            original_year = d.year
        except ValueError:
            flash("Invalid date format.", "error")
            return redirect(url_for("settings_dates"))

        db.save_special_date(
            name, date_md, enabled=True, emoji=emoji,
            original_year=original_year, is_custom=True, recurring=recurring,
        )
        flash(f"Added \"{name}\"!", "success")
        return redirect(url_for("settings_dates"))

    @app.route("/settings/special-dates/<int:date_id>/edit", methods=["GET", "POST"])
    def settings_date_edit(date_id):
        if not db.is_setup_complete():
            return redirect(url_for("index"))

        sd = db.get_special_date(date_id)
        if not sd:
            flash("Date not found.", "error")
            return redirect(url_for("settings_dates"))

        if request.method == "POST":
            name = request.form.get("name", "").strip()[:50]
            date_val = request.form.get("date_val", "").strip()
            emoji = request.form.get("emoji", "\u2764\ufe0f").strip()
            recurring = request.form.get("recurring", "1") == "1"

            if not name or not date_val:
                flash("Name and date are required.", "error")
                return redirect(url_for("settings_date_edit", date_id=date_id))

            try:
                d = date.fromisoformat(date_val)
                date_md = f"{d.month:02d}/{d.day:02d}"
                original_year = d.year
            except ValueError:
                flash("Invalid date format.", "error")
                return redirect(url_for("settings_date_edit", date_id=date_id))

            db.update_special_date(date_id, name, date_md, emoji, original_year, recurring)
            flash(f"Updated \"{name}\"!", "success")
            return redirect(url_for("settings_dates"))

        # Build full_date for the edit form
        parsed = _parse_date_md(sd["date_md"])
        if parsed and sd.get("original_year"):
            m, dy = parsed
            sd["full_date"] = date(sd["original_year"], m, min(dy, 28)).isoformat()
        else:
            sd["full_date"] = ""

        return render_template(
            "settings_date_form.html",
            editing=True,
            date_obj=sd,
            emoji_choices=_emoji_choices(),
        )

    @app.route("/settings/special-dates/<int:date_id>/delete", methods=["POST"])
    def settings_date_delete(date_id):
        sd = db.get_special_date(date_id)
        if sd:
            db.delete_special_date(date_id)
            flash(f"Deleted \"{sd['occasion_name']}\".", "success")
        return redirect(url_for("settings_dates"))

    return app


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _build_card_deck(gifts: list[dict], pool_type: str) -> list[dict]:
    """Build JSON-serializable card deck from gift suggestions."""
    deck = []
    for g in gifts:
        card = {
            "name": g["name"],
            "tags": g.get("tags", [])[:3],
            "effort": g.get("effort", 1),
            "gift_type": pool_type,
            "price": g.get("price", ""),
            "kind": g.get("kind", "product"),
        }
        if card["kind"] == "product":
            card["top_pick_name"] = g.get("top_pick_name", "")
            card["top_pick_url"] = g.get("top_pick_url", "")
            query = g.get("browse_query") or g["name"]
            card["browse_url"] = "https://www.amazon.com/s?k=" + quote_plus(query)
        else:
            card["venue_name"] = g.get("venue_name", "")
            card["venue_url"] = g.get("venue_url", "")
        deck.append(card)
    return deck


def _finish_setup(db, answers):
    partner_name = answers.get("partner_name", "Your Partner")
    db.save_profile(partner_name)

    for q in SETUP_QUESTIONS:
        answer = answers.get(q["key"], "")
        if answer:
            if q["category"] in ("giver", "occasions"):
                continue  # saved separately
            db.save_setup_answer(q["key"], q["text"], answer, q["category"])

    # Save giver profile answers
    giver_keys = [q["key"] for q in SETUP_QUESTIONS if q.get("category") == "giver"]
    if any(answers.get(k) for k in giver_keys):
        db.save_giver_profile(answers)

    # Save special dates from occasion answers
    _save_special_dates(db, answers)

    db.init_reminders()
    session.pop("setup_answers", None)
    return render_template("setup_complete.html", partner_name=partner_name)


def _save_special_dates(db, answers: dict):
    """Parse occasion answers and save special dates to DB."""
    birthday = answers.get("partner_birthday", "").strip()
    anniversary = answers.get("anniversary_date", "").strip()
    is_mother = answers.get("is_mother", "").strip()
    holidays = answers.get("holidays", "")

    # Save birthday
    if birthday:
        db.save_special_date("birthday", birthday)

    # Save anniversary
    if anniversary:
        db.save_special_date("anniversary", anniversary)

    # Parse selected holidays
    holiday_list = [h.strip() for h in holidays.split(",") if h.strip()]

    # Valentine's Day
    val_enabled = any("valentine" in h.lower() for h in holiday_list)
    if val_enabled:
        db.save_special_date("valentines", "02/14", enabled=True)

    # Mother's Day
    mom_enabled = ("Yes" in is_mother) or any("mother" in h.lower() for h in holiday_list)
    if mom_enabled:
        db.save_special_date("mothers_day", "05/01", enabled=True)  # calculated dynamically

    # Christmas
    xmas_enabled = any("christmas" in h.lower() for h in holiday_list)
    if xmas_enabled:
        db.save_special_date("christmas", "12/25", enabled=True)

    # Birthday and Anniversary are enabled if selected in holidays
    if birthday and any("birthday" in h.lower() for h in holiday_list):
        db.save_special_date("birthday", birthday, enabled=True)
    elif birthday:
        db.save_special_date("birthday", birthday, enabled=True)

    if anniversary and any("anniversary" in h.lower() for h in holiday_list):
        db.save_special_date("anniversary", anniversary, enabled=True)
    elif anniversary:
        db.save_special_date("anniversary", anniversary, enabled=True)


def _persist_bonus_answers(db, questions, answers):
    """Save any answered bonus questions to the database."""
    for q in questions:
        answer = answers.get(q["key"], "")
        if answer:
            db.save_setup_answer(q["key"], q["text"], answer, q["category"])


def _finish_bonus(db, questions, answers):
    _persist_bonus_answers(db, questions, answers)
    answered_count = len([a for a in answers.values() if a])
    session.pop("bonus_answers", None)
    return render_template("bonus_complete.html", answered=answered_count)


def _finish_checkin3(db, answers):
    for q in CHECKIN_3_QUESTIONS:
        answer = answers.get(q["key"], "")
        if answer:
            db.save_checkin_answer("3month", q["key"], q["text"], answer)

    budget_answer = answers.get("checkin3_budget", "")
    if budget_answer and budget_answer != "Perfect":
        giver = db.get_giver_profile()
        if giver:
            giver_answers = {
                "giver_style": giver["giver_style"],
                "giver_time": giver["time_budget"],
                "giver_monthly_budget": giver["monthly_budget"],
                "giver_quarterly_budget": giver["quarterly_budget"],
                "giver_gift_type": giver["gift_type_pref"],
                "giver_experience_comfort": giver["experience_comfort"],
                "giver_diy_comfort": giver["diy_comfort"],
                "giver_busy_handling": giver["busy_handling"],
            }
            if budget_answer == "I can spend more":
                budget_map = {
                    "Under $25": "$25 – $50",
                    "$25 – $50": "$50 – $100",
                    "$50 – $100": "$100+",
                }
                giver_answers["giver_monthly_budget"] = budget_map.get(
                    giver["monthly_budget"], giver["monthly_budget"]
                )
            elif budget_answer == "I'd like to spend less":
                budget_map = {
                    "$100+": "$50 – $100",
                    "$50 – $100": "$25 – $50",
                    "$25 – $50": "Under $25",
                }
                giver_answers["giver_monthly_budget"] = budget_map.get(
                    giver["monthly_budget"], giver["monthly_budget"]
                )
            db.save_giver_profile(giver_answers)

    session.pop("checkin3_answers", None)
    return redirect(url_for("checkin3_complete"))


def _finish_update(db, answers):
    for q in UPDATE_QUESTIONS:
        answer = answers.get(q["key"], "")
        if answer:
            db.save_update_answer(q["text"], answer)

    reminders = db.get_all_reminders()
    for r in reminders:
        if r["reminder_type"] == "update":
            db.advance_reminder(r["id"])
            break

    session.pop("update_answers", None)
    return redirect(url_for("update_complete"))


def _build_todo_items(cards: list[dict]) -> list[dict]:
    """Build a sorted to-do list from occasion cards.

    Include:
    - selected but not given
    - overdue (past date, not complete/skipped/given)
    - upcoming within 14 days with no selection yet
    """
    todos = []
    for c in cards:
        state = c.get("state", "")
        days = c.get("days_until", 999)

        # Skip terminal states
        if state in ("complete", "skipped", "given"):
            continue

        include = False
        # 1) Selected gift not yet given
        if state == "selected":
            include = True
        # 2) Overdue (past date, still active)
        elif days < 0 and state in ("upcoming", "planning", "selected"):
            include = True
        # 3) Upcoming within 14 days, no selection
        elif 0 <= days <= 14 and state in ("upcoming", "planning"):
            include = True

        if not include:
            continue

        # Determine urgency
        if days < 0:
            urgency = "overdue"
            urgency_label = f"{abs(days)} day{'s' if abs(days) != 1 else ''} OVERDUE"
        elif days <= 3:
            urgency = "urgent"
            urgency_label = c.get("days_label", f"in {days} days")
        else:
            urgency = "normal"
            urgency_label = c.get("days_label", f"in {days} days")

        # Build action label
        has_gift = bool(c.get("gift_selected"))
        if has_gift:
            action_label = "Buy " + c["gift_selected"]
        else:
            action_label = "Pick gift for " + c.get("date_display", "")

        todos.append({
            "id": c["id"],
            "icon": c.get("icon", "&#127873;"),
            "label": c.get("occasion_label", ""),
            "date_display": c.get("date_display", ""),
            "days_label": urgency_label,
            "urgency": urgency,
            "state": state,
            "gift_selected": c.get("gift_selected") or "",
            "gift_purchase_link": c.get("gift_purchase_link") or "",
            "action_label": action_label,
            "has_gift": has_gift,
        })

    # Sort: overdue first, then by days_until ascending
    urgency_order = {"overdue": 0, "urgent": 1, "normal": 2}
    todos.sort(key=lambda t: urgency_order.get(t["urgency"], 2))
    return todos


def _emoji_choices() -> list[str]:
    """Return a list of emoji options for the special dates picker."""
    return [
        "\U0001f495", "\U0001f339", "\U0001f48d", "\u2764\ufe0f", "\U0001f48e",
        "\U0001f3e0", "\U0001f497", "\u2708\ufe0f", "\U0001f436", "\U0001f393",
        "\U0001f3b5", "\U0001f31f", "\U0001f382", "\U0001f381", "\U0001f4f7",
        "\U0001f375", "\U0001f30d", "\U0001f308",
    ]


def _parse_date_md(md_str: str) -> tuple[int, int] | None:
    """Parse 'MM/DD' or 'MM-DD' into (month, day)."""
    for sep in ("/", "-"):
        if sep in md_str:
            parts = md_str.strip().split(sep)
            if len(parts) == 2:
                try:
                    return int(parts[0]), int(parts[1])
                except ValueError:
                    return None
    return None


def _process_custom_dates_form(db, form):
    """Process the special dates form from setup wizard."""
    # Get preset date data from the question definition
    from gift_reminder.data.questions import SETUP_QUESTIONS
    question = None
    for q in SETUP_QUESTIONS:
        if q.get("key") == "custom_dates":
            question = q
            break
    if not question:
        return

    presets = question.get("preset_dates", [])

    # Process checked preset dates
    checked = form.getlist("sd_checked")
    for idx_str in checked:
        try:
            idx = int(idx_str)
        except ValueError:
            continue
        if idx < 0 or idx >= len(presets):
            continue
        date_val = form.get(f"sd_date_{idx}", "").strip()
        if not date_val:
            continue
        preset = presets[idx]
        try:
            d = date.fromisoformat(date_val)
            date_md = f"{d.month:02d}/{d.day:02d}"
            db.save_special_date(
                preset["name"], date_md, enabled=True,
                emoji=preset["emoji"], original_year=d.year,
                is_custom=True, recurring=True,
            )
        except ValueError:
            continue

    # Process custom dates JSON
    custom_json = form.get("custom_dates_json", "[]")
    try:
        custom_dates = json.loads(custom_json)
    except (json.JSONDecodeError, TypeError):
        custom_dates = []

    for cd in custom_dates:
        name = cd.get("name", "").strip()[:50]
        date_val = cd.get("date", "").strip()
        emoji = cd.get("emoji", "\u2764\ufe0f")
        recurring = cd.get("recurring", "1") == "1"
        if not name or not date_val:
            continue
        try:
            d = date.fromisoformat(date_val)
            date_md = f"{d.month:02d}/{d.day:02d}"
            db.save_special_date(
                name, date_md, enabled=True, emoji=emoji,
                original_year=d.year, is_custom=True, recurring=recurring,
            )
        except ValueError:
            continue


def main():
    app = create_app()
    print("\n  Gift Reminder is running at http://localhost:5000\n")
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()
