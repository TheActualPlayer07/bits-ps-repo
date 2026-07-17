import json
from typing import List
from pydantic import BaseModel, Field
from src.config import get_groq_client, DEFAULT_MODEL
from src.ingestion import CompanyProfile
from src.mapping import StrategicMapping

# ==========================================================
# EXECUTIVE COPYWRITING SCHEMAS
# ==========================================================

class PitchVariant(BaseModel):
    angle_name: str = Field(
        description="Name of the executive priority targeted (e.g., 'Operational Simplicity', 'Risk & Resilience', 'Technical Debt Mitigation')."
    )
    why_this_angle: str = Field(
        description="Brief strategic explanation of why this persuasion angle is highly relevant for this specific company."
    )
    subject_line: str = Field(
        description="A quiet, curiosity-driven subject line under six words. Absolute zero sales language or exaggeration."
    )
    email_body: str = Field(
        description="The written email body. Highly natural, conversational, completely free of any structural labels, and under 220 words."
    )

class PitchOutput(BaseModel):
    selected_tone_level: float = Field(
        description="The tone level parameter used to generate this output (0.0 to 1.0)."
    )
    tone_description: str = Field(
        description="Brief description of the stylistic register matching the selected tone level."
    )
    variants: List[PitchVariant] = Field(
        description="Exactly three distinct persuasion variants."
    )
    best_variant: str = Field(
        description="The angle_name of the strongest overall variant for this specific prospect."
    )
    selection_rationale: str = Field(
        description="Reasoning explaining why this specific variant is the most logical choice for the target executive."
    )

# ==========================================================
# PERSUASION & TRANSLATION ENGINE
# ==========================================================

def draft_pitches(
    profile: CompanyProfile, 
    mapping: StrategicMapping, 
    tone_level: float = 0.50
) -> PitchOutput:
    """
    Transforms strategic diagnostic mapping data into three highly natural,
    conversational outreach pitches that are indistinguishable from 
    thoughtful human peer communication.
    """
    client = get_groq_client()

    # Generic definition of the stylistic spectrum based on our slider
    tone_matrix = """
    Our system maps the slider value (0.0 to 1.0) to these stylistic registers:
    - 0.0 to 0.15 (Conversational / Direct Message): Short sentences, active verbs, plain language, direct peer tone.
    - 0.20 to 0.35 (Technical Peer / Engineering): Highly analytical. Mentions systems architecture, engineering realities, and integration points.
    - 0.40 to 0.60 (Professional / Standard B2B): Balanced, polite, direct, business-focused.
    - 0.65 to 0.80 (Executive / C-Suite): Macro-strategic, quiet, confident. Focuses on organizational alignment, capacity, and velocity.
    - 0.85 to 1.0 (Highly Formal Consulting): Structured, clinical, using formal advisory syntax and vocabulary.
    """

    system_prompt = f"""
You are an elite, senior technology advisor and solutions architect. 
Your responsibility is to take a business diagnostic report and write three distinct, highly personalized email pitches.

Your sole goal is to start an organic conversation. Write as though you spent 20 minutes researching their system setup before writing a personal note.

CRITICAL WRITING PROTOCOLS:

1. THE INVISIBLE STRUCTURE:
   Do NOT output any headings, labels, or section markers (like "Observation:", "Business Problem:", "Why this recommendation:", etc.) inside the generated email body. 
   The structural sequence (Observation → Problem → Consequence → Recommended Service → Rationale → CTA) must be completely invisible and flow naturally through standard paragraphs.

2. ABSOLUTE TRACEABILITY (NO ACCIDENTAL HALLUCINATIONS):
   Do NOT invent percentages, money saved, ROI, latency improvements, timelines, maintenance costs, or statistics that are not explicitly present in the provided report. 
   If a number was not provided, do not use one. Never use placeholder stats like "improve by X%".

3. ZERO OUTREACH CLICHES:
   Never use pleasantries or standard sales openings (e.g., 'Hope you're doing well', 'My name is', 'I came across your company', 'We are industry leaders'). 
   Start the very first sentence immediately with a calm, neutral observation about their technology stack or structural environment.

4. REALISTIC SUBJECT LINES:
   Subject lines must be conversational, quiet, under six words, and driven by low-key curiosity. 
   Never promise results, sound promotional, or use exclamation marks.
   Excellent patterns:
   - Thoughts on your [topic] roadmap
   - Question about your [topic] strategy
   - One observation about your architecture
   - Curious about your [topic] transition

5. VALUE-DRIVEN CTA:
   Never ask for a call, a Zoom meeting, or a demo. Offer a peer-to-peer knowledge sharing resource instead.
   Excellent patterns:
   - I put together a brief reference architecture map illustrating this approach. Let me know if you'd like me to send it over.
   - I sketched a short comparison checklist for teams executing similar transitions. Happy to share it if it is useful.

6. TARGET SPECIFIC RECOMMENDATION:
   Every variant must focus completely on the single selected recommended service: "{mapping.executive_decision.recommended_service}". Do not suggest other service categories.

7. DO NOT DESIGN THE SOLUTION

Recommend the selected service category only.

Do NOT prescribe specific technologies, implementation approaches,
architectures, frameworks, standards, protocols or products unless they
already appear explicitly in the provided diagnostic report.

Avoid statements like:

- Implement FHIR
- Containerize workloads
- Introduce Kubernetes
- Build a Master Patient Index

Instead describe outcomes at the service level.

Example:

GOOD
"Modernizing the legacy platform would reduce the operational friction created by maintaining multiple disconnected systems."

BAD
"Implementing a FHIR integration layer with Kubernetes-backed microservices..."

8. HUMAN WRITING TEST

Before finalizing every email ask yourself:

"Would an experienced engineer actually write this sentence?"

If the answer is no,

rewrite it.

Prefer simple language over impressive language.

Avoid sounding like a consulting report.

Avoid sounding like ChatGPT.

9. AVOID CORPORATE FLUFF

Avoid generic phrases like:

- unlock value
- leverage
- best-in-class
- transformative
- cutting-edge
- game-changing
- maximize ROI
- accelerate innovation
- drive digital transformation
- seamless

Replace abstract language with concrete observations.

10. HANDLE UNCERTAINTY EXPLICITLY

If evidence is incomplete,

describe the possibility rather than stating it as fact.

Prefer

"This often creates..."

"It may lead to..."

"I suspect..."

"It is common for..."

instead of

"This causes..."

"It reduces..."

"It increases..."

Do not express speculation as certainty.

11. CONVERSATION TEST

Imagine the recipient replies,

"Interesting. Why do you think that?"

Every statement in the email should be defensible using only the provided profile and diagnostic report.

If you could not justify the statement,

remove it.

12. DISTINGUISH OBSERVATION FROM INFERENCE

Every technical statement in the email must fall into exactly one category.

Observation:
A fact directly present in the supplied information.

Inference:
A reasonable conclusion drawn from one or more observations.

Never present an inference as though it were an observation.

Example:

Observation:
"The company is migrating to Epic while still operating Cerner and Meditech."

Inference:
"Transitions like this often create interoperability challenges."

Bad:
"Your migration is already causing widespread interoperability failures."

The reader should always be able to tell which statements are factual observations and which are professional interpretations.

13. NATURAL CONVERSATION & CTA

The email should feel like it was written by someone who genuinely noticed something interesting—not someone trying to sell immediately.

The objective is NOT to close a deal.

The objective is simply to earn a thoughtful reply.

Write as though you are sharing an observation with another experienced technology leader.

Avoid sounding rehearsed or overly polished.

--------------------------------------------------

CTA WRITING RULES

The CTA should feel like something you already happened to create.

It should never sound like you are producing something specifically to make a sale.

Avoid phrases such as:

- I've prepared...
- I've drafted...
- We created...
- Our team developed...
- We can build...
- We can help...
- Would you like to schedule...
- Can we arrange a demo...

These sound like sales outreach.

Instead, write naturally, as if referring to something that already exists.

Examples:

GOOD

"I ended up sketching a one-page reference architecture while thinking about this. Happy to send it over if it'd be useful."

"I put together a short comparison of the approaches teams usually take during transitions like this. Let me know if you'd like a copy."

"I recently documented a few integration patterns that seem to work well in environments like yours. Happy to send them over."

"I have a short interoperability checklist that might be useful if you're evaluating different modernization paths."

"I wrote down a few observations after seeing similar migrations. Happy to share them if they're helpful."

Notice that these sound like one engineer sharing useful material with another.

Never sound like you're offering a product brochure.

--------------------------------------------------

CONVERSATION TEST

Before finalizing the email, imagine the recipient replies:

"That's interesting... why did you think of us?"

The email should naturally answer that question through its observations.

Then imagine they reply:

"Can you send that over?"

If the CTA naturally leads to that response, it is good.

If the CTA feels like a disguised sales meeting request, rewrite it.

--------------------------------------------------

FINAL HUMAN TEST

Read the finished email one last time.

If it sounds like:

- a consulting report
- ChatGPT
- LinkedIn marketing
- SDR outreach
- corporate copywriting

rewrite it.

The email should instead feel like a thoughtful note from a senior architect who noticed something worth mentioning and decided to reach out.


STYLE spectrum details:
{tone_matrix}
"""

    user_prompt = f"""
Draft three distinct persuasive variants based on the company's profile and diagnostic analysis.

TARGET PROFILE:
{json.dumps(profile.model_dump(), indent=2)}

DIAGNOSTIC REPORT:
{json.dumps(mapping.model_dump(), indent=2)}

REQUESTED TONE LEVEL SLIDER VALUE: {tone_level}

The three variants should represent different executive perspectives:
- Variant 1: Operational Simplicity (Focusing on day-to-day workflow bottleneck reduction)
- Variant 2: Risk & Resilience (Focusing on safety, continuity, compliance, and disaster prevention)
- Variant 3: Future Scalability / Technical Debt (Focusing on removing friction to support expansion)

Return exactly one valid JSON object structured like this:
{{
  "selected_tone_level": {tone_level},
  "tone_description": "...",
  "variants": [
    {{
      "angle_name": "...",
      "why_this_angle": "...",
      "subject_line": "...",
      "email_body": "..."
    }},
    {{
      "angle_name": "...",
      "why_this_angle": "...",
      "subject_line": "...",
      "email_body": "..."
    }},
    {{
      "angle_name": "...",
      "why_this_angle": "...",
      "subject_line": "...",
      "email_body": "..."
    }}
  ],
  "best_variant": "...",
  "selection_rationale": "..."
}}
"""

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        # We hold the temperature strictly at 0.35 as requested for precise data tracing
        temperature=0.15  
    )

    raw_response = response.choices[0].message.content
    if raw_response is None:
        raise RuntimeError("Groq returned an empty response during pitch drafting.")

    try:
        parsed = json.loads(raw_response)
        return PitchOutput(**parsed)
    except Exception as e:
        print("\n[ERROR] Failed to parse generated pitches into PitchOutput schema.\n")
        print("Raw Output:")
        print(raw_response)
        raise e

# ==========================================================
# END-TO-END PIPELINE SYSTEM TEST
# ==========================================================

if __name__ == "__main__":
    from src.inference import analyze_company
    from src.ingestion import load_profile
    from src.mapping import map_services

    test_file = "data/Sample_profile.json"

    print("=" * 80)
    print("                 EXECUTING COMPLETE AGENT WORKFLOW                      ")
    print("=" * 80)

    print("\n[Step 1] Loading raw enterprise data...")
    profile = load_profile(test_file)

    print("[Step 2] Executing diagnostic problem inference...")
    analysis = analyze_company(profile)

    print("[Step 3] Architecting vendor-agnostic solution mapping...")
    mapping_result = map_services(analysis)

    # We will run this with an 'Executive / CIO' tone level of 0.75
    target_slider = 0.75
    print(f"[Step 4] Drafting targeted outreach (Tone Slider: {target_slider})...")
    pitches = draft_pitches(profile, mapping_result, tone_level=target_slider)

    print("\n" + "=" * 80)
    print("                      GENERATED OUTREACH CAMPAIGN SUMMARY                       ")
    print("========================================================================")
    print(f"Applied Slider Setting: {pitches.selected_tone_level} ({pitches.tone_description})\n")

    for i, var in enumerate(pitches.variants, start=1):
        print(f"\n({i}) PERSUASION ANGLE: {var.angle_name.upper()}")
        print("-" * 80)
        print(f"Strategic Rationale: {var.why_this_angle}")
        print(f"Subject Line        : {var.subject_line}")
        print("\nEmail Body:")
        print(var.email_body)
        print("-" * 80)

    print("\n" + "=" * 80)
    print("                             STRATEGIC DECISION                         ")
    print("========================================================================")
    print(f"HIGH-CONVERSION CHOICE: {pitches.best_variant}")
    print(f"Selection Justification:\n{pitches.selection_rationale}")
    print("=" * 80 + "\n")