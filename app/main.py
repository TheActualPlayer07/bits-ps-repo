"""
Flask app entry point. Two routes:
  GET  /        -> samples fresh questions, stores the ids in session, renders the intake form
  POST /submit  -> reassembles form data, validates it against the session's sampled ids,
                   runs the full scoring pipeline, renders the results page

Run: python -m app.main  (or `flask --app app.main run` )
Requires GROQ_API_KEY in the environment for the LLM-graded categories to work live;
without it, those categories fall back to a flagged neutral default (see aggregator.py).
"""
import os
from dotenv import load_dotenv
load_dotenv()  # reads a .env file in the project root, if present — does nothing if it doesn't exist

from flask import Flask, render_template, request, session, redirect, url_for

from app.aggregator import build_intake_samples, run_full_scoring
from app.action_plan import generate_action_plan
from app.scoring.deterministic import ALL_PATTERNS, CS_TOPICS

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me-before-deploying")


@app.route("/", methods=["GET"])
def index():
    samples = build_intake_samples()
    # Store only the sampled ids server-side, so submission can be validated
    # against what was actually shown rather than trusting the client blindly.
    session["aptitude_ids"] = [q["id"] for q in samples["aptitude_questions"]]
    session["dsa_ids"] = [q["id"] for q in samples["dsa_questions"]]
    session["hr_ids"] = [q["id"] for q in samples["hr_questions"]]

    return render_template(
        "intake.html",
        aptitude_questions=samples["aptitude_questions"],
        dsa_questions=samples["dsa_questions"],
        hr_questions=samples["hr_questions"],
        all_patterns=sorted(ALL_PATTERNS),
        cs_topics=CS_TOPICS,
    )


@app.route("/submit", methods=["POST"])
def submit():
    form = request.form

    # ---- Integrity check: only grade questions that were actually sampled this session ----
    session_aptitude_ids = session.get("aptitude_ids", [])
    session_dsa_ids = session.get("dsa_ids", [])
    session_hr_ids = session.get("hr_ids", [])

    if not (session_aptitude_ids and session_dsa_ids and session_hr_ids):
        # Session expired or form was submitted without visiting "/" first
        return redirect(url_for("index"))

    aptitude_submitted = [
        {"question_id": qid, "selected_option_id": form.get(f"aptitude__{qid}")}
        for qid in session_aptitude_ids
    ]

    dsa_answers = {qid: form.get(f"dsa_answer__{qid}", "") for qid in session_dsa_ids}
    hr_answers = {qid: form.get(f"hr_answer__{qid}", "") for qid in session_hr_ids}

    form_data = {
        "months_remaining": float(form.get("months_remaining", 6)),
        "year": form.get("year"),

        "dsa": {
            "leetcode_easy": int(form.get("leetcode_easy", 0)),
            "leetcode_medium": int(form.get("leetcode_medium", 0)),
            "leetcode_hard": int(form.get("leetcode_hard", 0)),
            "patterns_known": form.getlist("patterns_known"),
        },
        "dsa_question_ids": session_dsa_ids,
        "dsa_answers": dsa_answers,

        "cs": {f"{topic}_known": form.getlist(f"{topic}_known") for topic in CS_TOPICS},

        "experience": {
            "has_internship": bool(form.get("has_internship")),
            "internship_relevant": bool(form.get("internship_relevant")),
            "internship_2plus_months": bool(form.get("internship_2plus_months")),
            "has_certification": bool(form.get("has_certification")),
            "certification_relevant": bool(form.get("certification_relevant")),
        },

        "resume": {"resume_checklist": form.getlist("resume_checklist")},

        "speed": {
            "easy_under_15min": bool(form.get("easy_under_15min")),
            "medium_under_35min": bool(form.get("medium_under_35min")),
            "hard_under_60min": bool(form.get("hard_under_60min")),
            "debugs_independently": bool(form.get("debugs_independently")),
            "writes_clean_code": bool(form.get("writes_clean_code")),
        },

        "projects": {"project_checklist": form.getlist("project_checklist")},
        "project_description": form.get("project_description", ""),

        "explanation_answer": form.get("explanation_answer", ""),

        "aptitude_submitted": aptitude_submitted,

        "hr_question_ids": session_hr_ids,
        "hr_answers": hr_answers,
    }

    result = run_full_scoring(form_data)
    plan = generate_action_plan(result)

    return render_template("results.html", result=result, plan=plan)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
