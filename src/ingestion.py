import json
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CompanyProfile(BaseModel):
    """
    Structured company profile used throughout the outreach pipeline.
    """

    # ----------------------------
    # REQUIRED
    # ----------------------------
    company_name: str
    website: Optional[str] = None

    # ----------------------------
    # IMPORTANT (usually available)
    # ----------------------------
    industry: Optional[str] = None
    company_size: Optional[str] = None
    headquarters: Optional[str] = None
    founded_year: Optional[int] = None

    # ----------------------------
    # OUTREACH RESEARCH
    # ----------------------------
    business_summary: Optional[str] = None
    target_problem: Optional[str] = None
    value_proposition: Optional[str] = None

    products_services: List[str] = Field(default_factory=list)
    tech_stack: List[str] = Field(default_factory=list)
    competitors: List[str] = Field(default_factory=list)

    # ----------------------------
    # RECENT SIGNALS
    # ----------------------------
    recent_news: List[str] = Field(default_factory=list)

    hiring_roles: List[str] = Field(default_factory=list)

    recent_funding: Optional[str] = None

    recent_events: List[str] = Field(default_factory=list)

    # ----------------------------
    # CONTACT
    # ----------------------------
    linkedin_url: Optional[str] = None

    contact_name: Optional[str] = None

    contact_role: Optional[str] = None

    # ----------------------------
    # SOCIAL PROOF
    # ----------------------------
    notable_customers: List[str] = Field(default_factory=list)

    awards: List[str] = Field(default_factory=list)

    # ----------------------------
    # AI NOTES
    # ----------------------------
    outreach_angle: Optional[str] = None

    personalization_notes: List[str] = Field(default_factory=list)

    confidence_score: Optional[float] = None

    # ----------------------------
    # EVERYTHING UNKNOWN
    # ----------------------------
    metadata: Dict[str, Any] = Field(default_factory=dict)


def load_profile(file_path: str) -> CompanyProfile:

    with open(file_path, "r", encoding="utf-8") as file:
        raw_data = json.load(file)

    return CompanyProfile(**raw_data)


if __name__ == "__main__":

    sample_path = "data/Sample_profile.json"

    try:

        profile = load_profile(sample_path)

        print("=" * 40)
        print("Profile Loaded Successfully")
        print("=" * 40)

        print(f"Company : {profile.company_name}")
        print(f"Industry : {profile.industry}")
        print(f"Website : {profile.website}")
        print(f"Products : {profile.products_services}")
        print(f"Tech Stack : {profile.tech_stack}")
        print(f"Recent News : {profile.recent_news}")
        print(f"Target Problem : {profile.target_problem}")
        print(f"Metadata : {profile.metadata}")

    except Exception as e:
        print("Validation Failed")
        print(e)