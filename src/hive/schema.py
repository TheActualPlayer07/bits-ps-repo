from pydantic import BaseModel


class SourcedField(BaseModel):
    value: str | None = None
    source: str | None = None  # URL the fact was grounded in


class FundingRound(BaseModel):
    round_type: str | None = None
    amount: str | None = None
    date: str | None = None
    source: str | None = None


class Product(BaseModel):
    name: str | None = None
    description: str | None = None
    source: str | None = None


class NewsItem(BaseModel):
    headline: str | None = None
    date: str | None = None
    summary: str | None = None
    source: str | None = None


class Contact(BaseModel):
    name: str | None = None
    role: str | None = None
    contact_method: str | None = None  # e.g. LinkedIn URL, email
    source: str | None = None


class CompletenessVerdict(BaseModel):
    is_complete: bool = False
    missing_fields: list[str] = []
    notes: str | None = None


class CompanyProfile(BaseModel):
    # Intake
    input_name: str
    canonical_name: str | None = None

    # Discovery
    industry: SourcedField = SourcedField()
    description: SourcedField = SourcedField()
    company_size: SourcedField = SourcedField()
    location: SourcedField = SourcedField()

    # Enrichment
    funding: list[FundingRound] = []
    products: list[Product] = []
    recent_news: list[NewsItem] = []

    # Relevance + contact
    relevance_to_student: str | None = None
    contact: Contact = Contact()

    # Completeness
    completeness: CompletenessVerdict = CompletenessVerdict()
