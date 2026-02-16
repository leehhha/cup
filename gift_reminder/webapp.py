"""Flask web application for Gift Reminder."""

import json
import os
import secrets
from datetime import date, datetime

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for

from gift_reminder.data.questions import BONUS_QUESTIONS, SETUP_QUESTIONS, UPDATE_QUESTIONS
from gift_reminder.database import Database
from gift_reminder.gift_engine import GiftEngine


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
    # Root
    # ------------------------------------------------------------------
    @app.route("/")
    def index():
        if db.is_setup_complete():
            return redirect(url_for("dashboard"))
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

        # Load saved answers from session
        answers = session.get("setup_answers", {})

        if request.method == "POST":
            answer = request.form.get("answer", "").strip()
            if answer:
                answers[question["key"]] = answer
                session["setup_answers"] = answers

            # Last question -> finish
            if index == total - 1:
                return _finish_setup(db, answers)

            return redirect(url_for("setup_question", index=index + 1))

        # GET
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
    # Dashboard
    # ------------------------------------------------------------------
    @app.route("/dashboard")
    def dashboard():
        if not db.is_setup_complete():
            return redirect(url_for("index"))

        profile = db.get_profile()
        partner_name = profile["partner_name"]

        due_reminders = db.get_due_reminders()
        active_reminders = [r for r in due_reminders if r["reminder_type"] in ("monthly", "quarterly")]
        update_due = any(r["reminder_type"] == "update" for r in due_reminders)

        monthly_gifts = engine.suggest_monthly_gifts(5)
        quarterly_gifts = engine.suggest_quarterly_gifts(3)

        # Build a combined card deck for the swipe UI
        card_deck = []
        for g in monthly_gifts:
            card_deck.append({
                "name": g["name"],
                "tags": g.get("tags", [])[:3],
                "effort": g.get("effort", 1),
                "gift_type": "monthly",
            })
        for g in quarterly_gifts:
            card_deck.append({
                "name": g["name"],
                "tags": g.get("tags", [])[:3],
                "effort": g.get("effort", 2),
                "gift_type": "quarterly",
            })
        card_deck_json = json.dumps(card_deck)

        gifts = db.get_recent_gifts(10)
        for g in gifts:
            try:
                d = datetime.fromisoformat(g["date_given"])
                g["date_display"] = d.strftime("%b %d")
            except (ValueError, TypeError):
                g["date_display"] = g["date_given"][:10] if g["date_given"] else "?"

        reminders = db.get_all_reminders()
        today = date.today()
        for r in reminders:
            try:
                d = date.fromisoformat(r["next_due"])
                days_until = (d - today).days
                if days_until <= 0:
                    r["due_display"] = "Due now!"
                    r["due_class"] = "due-now"
                elif days_until <= 7:
                    r["due_display"] = f"In {days_until} days"
                    r["due_class"] = "due-soon"
                else:
                    r["due_display"] = d.strftime("%B %d, %Y")
                    r["due_class"] = "due-later"
            except (ValueError, TypeError):
                r["due_display"] = r["next_due"]
                r["due_class"] = "due-later"

        # Bonus questions remaining
        answered_keys = db.get_answered_question_keys()
        bonus_remaining = len([q for q in BONUS_QUESTIONS if q["key"] not in answered_keys])

        return render_template(
            "dashboard.html",
            partner_name=partner_name,
            active_reminders=active_reminders,
            update_due=update_due,
            monthly_gifts=monthly_gifts,
            quarterly_gifts=quarterly_gifts,
            card_deck_json=card_deck_json,
            gifts=gifts,
            reminders=reminders,
            bonus_remaining=bonus_remaining,
        )

    # ------------------------------------------------------------------
    # Gift actions
    # ------------------------------------------------------------------
    @app.route("/log-suggestion")
    def log_suggestion():
        name = request.args.get("name", "")
        gift_type = request.args.get("gift_type", "monthly")
        if name:
            today = date.today().isoformat()
            db.add_gift(name, gift_type, "", today)
            flash("Gift logged!", "success")
        return redirect(url_for("dashboard"))

    @app.route("/log-gift", methods=["POST"])
    def log_gift():
        name = request.form.get("gift_name", "").strip()
        gift_type = request.form.get("gift_type", "monthly")
        rating = request.form.get("rating", "0")
        notes = request.form.get("notes", "").strip()

        if not name:
            flash("Please enter a gift name.", "error")
            return redirect(url_for("dashboard"))

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
        return redirect(url_for("dashboard"))

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

    @app.route("/dismiss/<int:reminder_id>")
    def dismiss_reminder(reminder_id):
        db.advance_reminder(reminder_id)
        return redirect(url_for("dashboard"))

    # ------------------------------------------------------------------
    # Bonus questions
    # ------------------------------------------------------------------
    @app.route("/bonus")
    def bonus_intro():
        answered_keys = db.get_answered_question_keys()
        unanswered = [q for q in BONUS_QUESTIONS if q["key"] not in answered_keys]
        if not unanswered:
            flash("You've answered all bonus questions!", "success")
            return redirect(url_for("dashboard"))
        return render_template("bonus_intro.html", total=len(unanswered))

    @app.route("/bonus/<int:index>", methods=["GET", "POST"])
    def bonus_question(index):
        answered_keys = db.get_answered_question_keys()
        unanswered = [q for q in BONUS_QUESTIONS if q["key"] not in answered_keys]
        total = len(unanswered)

        if total == 0:
            return redirect(url_for("dashboard"))
        if index < 0 or index >= total:
            return redirect(url_for("bonus_intro"))

        question = unanswered[index]
        answers = session.get("bonus_answers", {})

        if request.method == "POST":
            answer = request.form.get("answer", "").strip()
            if answer:
                answers[question["key"]] = answer
                session["bonus_answers"] = answers

            # Last question -> finish
            if index == total - 1:
                return _finish_bonus(db, unanswered, answers)

            return redirect(url_for("bonus_question", index=index + 1))

        # GET
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
        return redirect(url_for("dashboard"))

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

    return app


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _finish_setup(db, answers):
    partner_name = answers.get("partner_name", "Your Partner")
    db.save_profile(partner_name)

    for q in SETUP_QUESTIONS:
        answer = answers.get(q["key"], "")
        if answer:
            db.save_setup_answer(q["key"], q["text"], answer, q["category"])

    db.init_reminders()
    session.pop("setup_answers", None)
    return render_template("setup_complete.html", partner_name=partner_name)


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
