import json

from typing import List

from pydantic import BaseModel, Field

from src.config import get_groq_client, DEFAULT_MODEL
from src.ingestion import CompanyProfile, load_profile


# ==========================================================
# OUTPUT SCHEMA
# ==========================================================

class InferredProblem(BaseModel):

    title: str = Field(
        description="A concise name for the inferred business problem."
    )

    root_cause: str = Field(
        description="The likely underlying cause of this problem."
    )

    evidence: str = Field(
        description="Evidence from the company profile supporting this diagnosis."
    )

    business_impact: str = Field(
        description="Operational or commercial consequences if this problem persists."
    )

    affected_departments: List[str] = Field(
        description="Business functions primarily affected."
    )

    severity: int = Field(
        description="Severity from 1 to 10."
    )

    confidence: float = Field(
        description="Confidence score between 0 and 1."
    )


class InferenceAnalysis(BaseModel):

    executive_summary: str = Field(
        description="Short executive summary."
    )

    underlying_theme: str = Field(
        description="The central business challenge connecting all problems."
    )

    diagnostic_summary: str = Field(
        description="Explain how the evidence connects to the inferred problems."
    )

    inferred_problems: List[InferredProblem]


# ==========================================================
# INFERENCE ENGINE
# ==========================================================

def analyze_company(profile: CompanyProfile) -> InferenceAnalysis:

    client = get_groq_client()

    system_prompt = """
You are a senior management consultant specializing in enterprise technology strategy,
operations, and digital transformation.

Your ONLY responsibility is diagnosis.

You are NOT a salesperson.

You are NOT a solution architect.

You are NOT a consultant trying to sell services.

You are preparing an internal executive assessment.

Rules:

1. Never invent facts.

2. Every diagnosis MUST reference evidence from the supplied company profile.

3. Infer hidden operational consequences rather than simply repeating facts.

4. Combine multiple signals before drawing conclusions.

5. Never recommend products.

6. Never recommend vendors.

7. Never recommend services.

8. Never suggest solutions.

9. Return EXACTLY THREE inferred problems.

10. Order problems from highest confidence to lowest confidence.

11. Every problem must represent a DIFFERENT business issue.

12. Avoid generic statements that could apply to any company.

13. If evidence is weak, reduce the confidence score.

14. Return ONLY valid JSON.

15. Every inferred problem should explain WHY the evidence leads to that diagnosis,
not merely restate information from the company profile.

16. Think in terms of cause-and-effect chains.

Identify:

Evidence
↓

Root Cause
↓

Operational Consequence
↓

Business Impact

Your diagnosis should follow this reasoning structure.
"""

    user_prompt = f"""
Analyze the following company profile.

Your goal is NOT to summarize the profile.

Instead, identify hidden operational problems that are implied by the available evidence.

Every diagnosis should connect multiple pieces of information together.

Company Profile

{json.dumps(profile.model_dump(), indent=2)}

Return exactly one JSON object with the following structure:

{{
    "executive_summary": "...",

    "underlying_theme": "...",

    "diagnostic_summary": "...",

    "inferred_problems": [

        {{
            "title": "...",

            "root_cause": "...",

            "evidence": "...",

            "business_impact": "...",

            "affected_departments": [
                "...",
                "..."
            ],

            "severity": 8,

            "confidence": 0.91
        }}

    ]
}}
"""

    response = client.chat.completions.create(

        model=DEFAULT_MODEL,

        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],

        response_format={"type": "json_object"},

        temperature=0.1,
    )

    raw_response = response.choices[0].message.content

    if raw_response is None:
        raise RuntimeError("Groq returned an empty response.")

    try:

        parsed = json.loads(raw_response)

        return InferenceAnalysis(**parsed)

    except Exception as e:

        print("\nFailed to parse model output.\n")

        print(raw_response)

        raise e


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    sample_path = "data/Sample_profile.json"

    profile = load_profile(sample_path)

    print("=" * 50)
    print(f"Running inference for {profile.company_name}")
    print("=" * 50)

    analysis = analyze_company(profile)

    print("\nExecutive Summary")
    print("-" * 50)
    print(analysis.executive_summary)

    print("\nUnderlying Theme")
    print("-" * 50)
    print(analysis.underlying_theme)

    print("\nDiagnostic Summary")
    print("-" * 50)
    print(analysis.diagnostic_summary)

    print("\nProblems")
    print("-" * 50)

    for i, problem in enumerate(analysis.inferred_problems, start=1):

        print(f"\n{i}. {problem.title}")

        print(f"Root Cause         : {problem.root_cause}")

        print(f"Evidence           : {problem.evidence}")

        print(f"Business Impact    : {problem.business_impact}")

        print(f"Affected Teams     : {', '.join(problem.affected_departments)}")

        print(f"Severity           : {problem.severity}/10")

        print(f"Confidence         : {problem.confidence:.2f}")