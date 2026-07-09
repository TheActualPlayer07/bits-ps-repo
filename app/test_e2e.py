"""
End-to-end smoke test using Flask's test client. Simulates a full
GET / -> POST /submit cycle. No GROQ_API_KEY is set here, so the
LLM-graded categories should gracefully fall back rather than crash
the request — this test specifically verifies that failure path.

Run: python -m app.test_e2e
"""
import re
from app.main import app


def run():
    client = app.test_client()

    # ---- GET / : should render the intake form with sampled questions ----
    resp = client.get("/")
    assert resp.status_code == 200, f"GET / failed: {resp.status_code}"
    html = resp.get_data(as_text=True)
    assert "Placement Panic Meter" in html
    print("GET / — OK, form rendered")

    # Pull the sampled question ids straight out of the rendered form's hidden inputs
    dsa_ids = re.findall(r'name="dsa_question_ids" value="([^"]+)"', html)
    aptitude_ids = re.findall(r'name="aptitude_question_ids" value="([^"]+)"', html)
    hr_ids = re.findall(r'name="hr_question_ids" value="([^"]+)"', html)
    print(f"Sampled: {len(dsa_ids)} DSA, {len(aptitude_ids)} aptitude, {len(hr_ids)} HR questions")
    assert len(dsa_ids) == 4 and len(aptitude_ids) == 4 and len(hr_ids) == 3

    # Grab one valid aptitude option id per question from the rendered radios, so we submit a real answer
    aptitude_option_map = {}
    for qid in aptitude_ids:
        opts = re.findall(rf'name="aptitude__{qid}" value="([^"]+)"', html)
        aptitude_option_map[qid] = opts[0] if opts else "a"

    # ---- POST /submit : a mixed-strength fake profile ----
    form_payload = {
        "months_remaining": "3",
        "year": "3",
        "leetcode_easy": "80", "leetcode_medium": "60", "leetcode_hard": "10",
        "patterns_known": ["arrays", "hashing", "two_pointers"],
        "os_known": ["deadlock", "paging"],
        "dbms_known": ["indexing"],
        "cn_known": [],
        "oop_known": ["inheritance", "polymorphism"],
        "has_internship": "1", "internship_relevant": "1",
        "project_checklist": ["clean_readme", "public_github"],
        "project_description": "A URL shortener with custom base-62 encoding and click analytics.",
        "resume_checklist": ["one_page", "clean_formatting"],
        "easy_under_15min": "1", "medium_under_35min": "1",
        "explanation_answer": "I used a hash map for O(1) lookups because the problem needed frequent existence checks; the tradeoff is O(n) extra space.",
    }
    for qid in dsa_ids:
        form_payload[f"dsa_answer__{qid}"] = "I'd use two pointers moving from both ends, giving O(n) time."
        form_payload.setdefault("dsa_question_ids", []).append(qid) if False else None
    for qid in hr_ids:
        form_payload[f"hr_answer__{qid}"] = "I want to grow and learn and make an impact."  # deliberately generic/cliche

    # Flask test client needs multi-value fields passed as a list of tuples for hidden inputs + checkboxes
    from werkzeug.datastructures import MultiDict
    multi_payload = MultiDict()
    for k, v in form_payload.items():
        if isinstance(v, list):
            for item in v:
                multi_payload.add(k, item)
        else:
            multi_payload.add(k, v)
    for qid in dsa_ids:
        multi_payload.add("dsa_question_ids", qid)
    for qid in aptitude_ids:
        multi_payload.add("aptitude_question_ids", qid)
        multi_payload.add(f"aptitude__{qid}", aptitude_option_map[qid])
    for qid in hr_ids:
        multi_payload.add("hr_question_ids", qid)

    resp = client.post("/submit", data=multi_payload)
    assert resp.status_code == 200, f"POST /submit failed: {resp.status_code}\n{resp.get_data(as_text=True)[:500]}"
    result_html = resp.get_data(as_text=True)
    assert "Your Panic Score" in result_html
    assert "Your priority fixes" in result_html
    print("POST /submit — OK, results page + action plan rendered")

    # Confirm the LLM fallback path actually engaged (no GROQ_API_KEY set in this environment)
    assert "llm unavailable" in result_html.lower() or "llm_unavailable" in result_html.lower(), \
        "Expected LLM fallback note to appear somewhere in gap flags since no API key is set"
    print("LLM fallback path engaged correctly (no GROQ_API_KEY set) — OK")

    print("\nEnd-to-end smoke test PASSED.")


if __name__ == "__main__":
    run()
