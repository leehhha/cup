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
from gift_reminder.occasions import build_timeline


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
    @app.route("/timeline")
    @app.route("/dashboard")
    def timeline():
        if not db.is_setup_complete():
            return redirect(url_for("index"))

        profile = db.get_profile()
        partner_name = profile["partner_name"]

        tl = build_timeline(db)

        answered_keys = db.get_answered_question_keys()
        bonus_remaining = len([q for q in BONUS_QUESTIONS if q["key"] not in answered_keys])

        return render_template(
            "timeline.html",
            partner_name=partner_name,
            next_up=tl["next_up"],
            upcoming=tl["upcoming"],
            past=tl["past"],
            bonus_remaining=bonus_remaining,
        )

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
            gifts = engine.suggest_quarterly_gifts(8)
            pool_type = "quarterly"
        else:
            # monthly, birthday, anniversary, holidays all use monthly pool
            gifts = engine.suggest_monthly_gifts(8)
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


def main():
    app = create_app()
    print("\n  Gift Reminder is running at http://localhost:5000\n")
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()
