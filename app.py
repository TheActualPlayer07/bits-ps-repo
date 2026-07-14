import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st

from hive.pipeline import run_pipeline
from hive.schema import CompanyProfile, SourcedField
from hive.stages.intake import InvalidCompanyNameError


def _render_sourced_field(label: str, field: SourcedField) -> None:
    if field.value:
        st.write(f"**{label}:** {field.value}")
        if field.source:
            st.caption(f"Source: {field.source}")
    else:
        st.write(f"**{label}:** not found")


def render_profile(profile: CompanyProfile) -> None:
    st.header(profile.canonical_name or profile.input_name)

    verdict = profile.completeness
    if verdict.is_complete:
        st.success("This profile is complete.")
    else:
        st.warning("This profile is incomplete — see details below.")
    if verdict.missing_fields:
        st.write(f"**Missing:** {', '.join(verdict.missing_fields)}")
    if verdict.notes:
        st.write(f"**Reviewer notes:** {verdict.notes}")

    st.subheader("Overview")
    _render_sourced_field("Industry", profile.industry)
    _render_sourced_field("Description", profile.description)
    _render_sourced_field("Company size", profile.company_size)
    _render_sourced_field("Location", profile.location)

    st.subheader("Funding")
    if profile.funding:
        for round_ in profile.funding:
            line = f"- {round_.round_type or 'Round'}: {round_.amount or 'undisclosed amount'}"
            if round_.date:
                line += f" ({round_.date})"
            st.write(line)
            if round_.source:
                st.caption(f"Source: {round_.source}")
    else:
        st.write("No funding information found.")

    st.subheader("Products")
    if profile.products:
        for product in profile.products:
            st.write(f"- **{product.name}**: {product.description or ''}")
    else:
        st.write("No product information found.")

    st.subheader("Recent news")
    if profile.recent_news:
        for item in profile.recent_news:
            st.write(f"- **{item.headline}** ({item.date or 'date unknown'})")
            if item.summary:
                st.write(item.summary)
            if item.source:
                st.caption(f"Source: {item.source}")
    else:
        st.write("No recent news found.")

    st.subheader("Why this company matters to you")
    st.write(profile.relevance_to_student or "Not available.")

    st.subheader("Contact")
    if profile.contact.name:
        st.write(f"**{profile.contact.name}** — {profile.contact.role or ''}")
        if profile.contact.contact_method:
            st.write(profile.contact.contact_method)
        if profile.contact.source:
            st.caption(f"Source: {profile.contact.source}")
    else:
        st.write("No specific, reachable contact found.")

    with st.expander("Raw profile JSON"):
        st.json(profile.model_dump())


st.set_page_config(page_title="HIVE — Company Research Agent", page_icon="🔍")
st.title("HIVE — Company Research Agent")
st.caption("Enter a company name to generate a sourced intelligence profile.")

company_name = st.text_input("Company name", placeholder="e.g. Notion")

if st.button("Research", type="primary"):
    if not company_name.strip():
        st.warning("Please enter a company name.")
    else:
        try:
            with st.spinner(f"Researching {company_name}..."):
                st.session_state.profile = run_pipeline(company_name)
        except InvalidCompanyNameError as e:
            st.session_state.pop("profile", None)
            st.error(str(e))
        except Exception as e:
            st.session_state.pop("profile", None)
            st.error(f"Something went wrong while researching this company: {e}")
            print(f"[HIVE] Unexpected error in run_pipeline: {e!r}")

if "profile" in st.session_state:
    render_profile(st.session_state.profile)
