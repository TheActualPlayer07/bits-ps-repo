import json
from typing import List
from pydantic import BaseModel, Field
from src.config import get_groq_client, DEFAULT_MODEL
from src.inference import InferenceAnalysis

# ==========================================================
# ENTERPRISE CONSULTING SCHEMAS
# ==========================================================

class CandidateService(BaseModel):
    service_name: str = Field(
        description="Concise, standardized consulting service name (e.g., 'Legacy Platform Modernization', 'Intelligent Document Processing'). No compound or long names."
    )
    category: str = Field(
        description="Broad industry vertical (e.g., Data Architecture, Process Automation, Cybersecurity)."
    )
    why_it_fits: str = Field(
        description="One-sentence explanation of why this service category is under consideration for the target client."
    )
    business_value: int = Field(
        ge=1, le=10,
        description="Strategic ROI and impact score (1-10)."
    )
    implementation_complexity: int = Field(
        ge=1, le=10,
        description="Technical and organizational implementation difficulty score (1-10)."
    )
    risk_reduction: int = Field(
        ge=1, le=10,
        description="Security, regulatory compliance, and system failure risk reduction score (1-10)."
    )
    time_to_value: str = Field(
        description="Expected time to see measurable operational improvement. Must be exactly 'Fast', 'Medium', or 'Long'."
    )

class RecommendationChain(BaseModel):
    current_situation: str = Field(
        description="Ultra-concise diagnostic summary of the current operating state bottlenecks."
    )
    recommended_service: str = Field(
        description="The chosen winner from the candidate pool."
    )
    what_changes: str = Field(
        description="Brief summary of the physical architecture or process changes that will take place."
    )
    expected_operational_improvements: List[str] = Field(
        description="Measurable operational metric improvements. Absolutely NO vague statements. Use exact terms like 'Reduced manual workflows', 'Faster record availability'."
    )
    expected_business_outcomes: List[str] = Field(
        description="Direct business benefits. Must be standard operational metrics like 'Reduced compliance exposure', 'Lower operational risk'."
    )
    risks_if_ignored: List[str] = Field(
        description="Specific legal, financial, or operational hazards of remaining in the status quo."
    )

class TraceabilityItem(BaseModel):
    problem: str = Field(description="The inferred problem title from the diagnostic report.")
    root_cause: str = Field(description="The underlying systemic or physical driver of the problem.")
    recommended_service: str = Field(description="The selected service class addressing this problem.")
    expected_resolution: str = Field(description="Clear explanation of how the recommended service neutralizes the root cause.")

class ExecutiveDecision(BaseModel):
    recommended_service: str = Field(
        description="The winning service class chosen."
    )
    priority: str = Field(
        description="The urgency of this intervention. Must be exactly: 'Critical', 'High', 'Medium', or 'Low'."
    )
    business_confidence: str = Field(
        description="Probability score percentage of implementation success (e.g., '85%')."
    )
    estimated_time_to_value: str = Field(
        description="Must be exactly: 'Fast', 'Medium', or 'Long'."
    )
    primary_reason: str = Field(
        description="One concise sentence explaining why this service was selected over every other candidate option."
    )

class StrategicMapping(BaseModel):
    candidates: List[CandidateService] = Field(
        description="Standardized portfolio of potential solution options evaluated."
    )
    ranked_services: List[str] = Field(
        description="The evaluated service names sorted in descending order of recommended priority."
    )
    why_selected_ranked_higher: str = Field(
        description="A concise comparative analysis explaining why the recommended service outranked the runners-up."
    )
    primary_recommendation: RecommendationChain = Field(
        description="The strategic reasoning chain formatted for immediate executive presentation."
    )
    traceability_matrix: List[TraceabilityItem] = Field(
        description="Unbroken chain of custody from identified problems down to concrete technical resolutions."
    )
    executive_decision: ExecutiveDecision = Field(
        description="Ultra-high-density final executive summary block."
    )

# ==========================================================
# REASONING & EVALUATION ENGINE
# ==========================================================

def map_services(analysis: InferenceAnalysis) -> StrategicMapping:
    """
    Acts as an independent, enterprise-grade technology strategy consulting firm.
    Analyzes systemic business issues and builds a cohesive, vendor-agnostic
    recommendation roadmap.
    """
    client = get_groq_client()

    system_prompt = """
You are a Senior Partner and Enterprise Systems Architect at an elite global technology consulting firm.

Your responsibility is to analyze a client's diagnostic business report and architect the optimal enterprise solution. 
You must think and write like an independent strategic advisor. 

CRITICAL PROTOCOLS:
1. VENDOR AGNOSTIC: Do not mention specific cloud providers, proprietary products, or outsourcing vendors. Frame everything as standardized professional service categories (e.g., 'Legacy Platform Modernization', 'Data Platform Modernization', 'Intelligent Document Processing').
2. HIGH-DENSITY, CONCISE EXECUTIVE STYLE: Avoid narrative walls of text. Use highly structured, bulleted reasoning. Every sentence must deliver high-value technical or business analysis.
3. CRITICAL EVALUATION: Grade candidates with realistic complexity/value metrics. A legacy platform migration is always High Complexity; an automation workflow is usually Medium Complexity. Reflect this reality.
4. MEASURABLE OUTCOMES: Under outcomes, ban all vague phrases like 'better efficiency', 'improved digital transformation', or 'superior performance'. Use concrete, operationally descriptive metrics (e.g., 'Reduced manual workflows', 'Lower operational risk', 'Faster record availability').
5. JSON COMPLIANCE: Return ONLY a single, valid JSON object matching the requested schema. No explanations outside the JSON block.
"""

    user_prompt = f"""
Analyze the diagnostic report below. Develop a strategic, vendor-agnostic consulting proposal.

DIAGNOSTIC REPORT:
{json.dumps(analysis.model_dump(), indent=2)}

Return a single JSON object structured exactly like this:
{{
  "candidates": [
    {{
      "service_name": "...",
      "category": "...",
      "why_it_fits": "...",
      "business_value": 9,
      "implementation_complexity": 8,
      "risk_reduction": 7,
      "time_to_value": "Medium"
    }}
  ],
  "ranked_services": ["Winning Service", "Runner-up Service 1", "Runner-up Service 2"],
  "why_selected_ranked_higher": "...",
  "primary_recommendation": {{
    "current_situation": "...",
    "recommended_service": "...",
    "what_changes": "...",
    "expected_operational_improvements": ["..."],
    "expected_business_outcomes": ["..."],
    "risks_if_ignored": ["..."]
  }},
  "traceability_matrix": [
    {{
      "problem": "...",
      "root_cause": "...",
      "recommended_service": "...",
      "expected_resolution": "..."
    }}
  ],
  "executive_decision": {{
    "recommended_service": "...",
    "priority": "Critical",
    "business_confidence": "85%",
    "estimated_time_to_value": "Medium",
    "primary_reason": "..."
  }}
}}
"""

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.1
    )

    raw_response = response.choices[0].message.content
    if raw_response is None:
        raise RuntimeError("Groq returned an empty response during evaluation.")

    try:
        parsed = json.loads(raw_response)
        return StrategicMapping(**parsed)
    except Exception as e:
        print("\n[ERROR] Failed to parse consulting recommendation into StrategicMapping schema.\n")
        print("Raw LLM Output:")
        print(raw_response)
        raise e

# ==========================================================
# REPORT PRESENTATION BLOCK
# ==========================================================

if __name__ == "__main__":
    from src.inference import analyze_company
    from src.ingestion import load_profile

    # We will run this against our legacy hospital network profile
    test_file = "data/Sample_profile.json"

    print("=" * 70)
    print(f"LOADING ENTERPRISE DATASET: {test_file}")
    print("=" * 70)
    profile = load_profile(test_file)

    print("\n[STEP 1] Generating Systemic Problem Diagnosis...")
    analysis = analyze_company(profile)

    print("\n[STEP 2] Running Strategy Architecture & Evaluation Engine...")
    report = map_services(analysis)

    print("\n" + "=" * 80)
    print("                      STRATEGIC ARCHITECTURE REPORT                      ")
    print("========================================================================")
    
    print("\n[A] SOLUTIONS PORTFOLIO EVALUATION")
    print("-" * 80)
    for cand in report.candidates:
        print(f"Service: {cand.service_name:<30} | Domain: {cand.category}")
        print(f"  └─ Why Fits  : {cand.why_it_fits}")
        print(f"  └─ Metrics   : Value: {cand.business_value}/10 | Complexity: {cand.implementation_complexity}/10 | Risk Mitigation: {cand.risk_reduction}/10")
        print(f"  └─ Velocity  : Time-to-Value: {cand.time_to_value}\n")

    print("\n[B] STRATEGIC RANKING & COMPARATIVE ANALYSIS")
    print("-" * 80)
    for i, name in enumerate(report.ranked_services, start=1):
        print(f" Rank {i}: {name}")
    print(f"\nDecision Justification:\n{report.why_selected_ranked_higher}")

    print("\n[C] PRIMARY ARCHITECTURAL RECOMMENDATION")
    print("-" * 80)
    rec = report.primary_recommendation
    print(f"CURRENT STATE : {rec.current_situation}")
    print(f"PROPOSED PATH : {rec.recommended_service}")
    print(f"WHAT CHANGES  : {rec.what_changes}")
    
    print("\nOperational Improvements:")
    for imp in rec.expected_operational_improvements:
        print(f"  → {imp}")
        
    print("\nBusiness Outcomes:")
    for out in rec.expected_business_outcomes:
        print(f"  ✓ {out}")

    print("\nRisks of Maintaining Status Quo:")
    for risk in rec.risks_if_ignored:
        print(f"  ⚠ {risk}")

    print("\n[D] TECHNICAL TRACEABILITY MATRIX")
    print("-" * 80)
    for item in report.traceability_matrix:
        print(f"PROBLEM   : {item.problem}")
        print(f"  └─ Root Cause: {item.root_cause}")
        print(f"  └─ Solution  : {item.recommended_service}")
        print(f"  └─ Resolution: {item.expected_resolution}\n")

    print("\n[E] EXECUTIVE DECISION SUMMARY (CIO CHEAT SHEET)")
    print("=" * 80)
    dec = report.executive_decision
    print(f"RECOMMENDED INTERVENTION: {dec.recommended_service}")
    print(f"IMPLEMENTATION PRIORITY : {dec.priority.upper()}")
    print(f"BUSINESS CONFIDENCE     : {dec.business_confidence}")
    print(f"ESTIMATED TIME TO VALUE : {dec.estimated_time_to_value}")
    print(f"PRIMARY SELECTION REASON: {dec.primary_reason}")
    print("=" * 80 + "\n")