import os
import json
import streamlit as st
from dotenv import load_dotenv

# Import backend schemas and processors (No modifications to backend files)
from src.ingestion import CompanyProfile
from src.inference import analyze_company
from src.mapping import map_services
from src.drafting import draft_pitches

# Load secret configurations
load_dotenv()

# Set up page configurations (Professional, clean internal tool style)
st.set_page_config(
    page_title="Outreach Agent Console",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# SESSION STATE INITIALIZATION
# ==========================================================
if "profile" not in st.session_state:
    st.session_state.profile = None
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "mapping" not in st.session_state:
    st.session_state.mapping = None
if "pitches" not in st.session_state:
    st.session_state.pitches = None

if "stage_load" not in st.session_state:
    st.session_state.stage_load = "Pending"
if "stage_inference" not in st.session_state:
    st.session_state.stage_inference = "Pending"
if "stage_mapping" not in st.session_state:
    st.session_state.stage_mapping = "Pending"
if "stage_drafting" not in st.session_state:
    st.session_state.stage_drafting = "Pending"

# ==========================================================
# SIDEBAR CONTROL & CONFIGURATION LAYER
# ==========================================================
st.sidebar.markdown("### ⚙️ Controls")

uploaded_file = st.sidebar.file_uploader(
    "Upload Company Profile (JSON)", 
    type=["json"]
)

# Process Uploaded File Safely
if uploaded_file is not None:
    try:
        raw_json = json.load(uploaded_file)
        validated_profile = CompanyProfile.model_validate(raw_json)
        st.session_state.profile = validated_profile
        st.session_state.stage_load = "Complete"
    except Exception as e:
        st.sidebar.error(f"Data Validation Failed:\n{e}")
        st.session_state.profile = None
        st.session_state.stage_load = "Failed"
else:
    st.session_state.profile = None
    st.session_state.stage_load = "Pending"

st.sidebar.markdown("---")

# Dynamic Tone Slider
def get_tone_label(val: float) -> str:
    if val <= 0.15:
        return "Conversational"
    elif val <= 0.35:
        return "Technical Peer"
    elif val <= 0.60:
        return "Professional"
    elif val <= 0.80:
        return "Executive"
    else:
        return "Formal Consulting"

selected_val = st.sidebar.slider(
    "Tone Slider",
    min_value=0.0,
    max_value=1.0,
    value=0.50,
    step=0.05,
    label_visibility="collapsed"
)
st.sidebar.markdown(f"**Tone:** {get_tone_label(selected_val)} ({selected_val:.2f})")

st.sidebar.markdown("---")

run_triggered = st.sidebar.button("Run Agent", use_container_width=True, type="primary")

st.sidebar.markdown("### Pipeline Status")

def get_status_icon(status: str) -> str:
    if status == "Complete":
        return "✓"
    elif status == "In-Progress":
        return "↻"
    elif status == "Failed":
        return "✕"
    return "○"

status_container = st.sidebar.container(border=True)
with status_container:
    st.markdown(f"{get_status_icon(st.session_state.stage_load)} Profile Loaded")
    st.markdown(f"{get_status_icon(st.session_state.stage_inference)} Inference")
    st.markdown(f"{get_status_icon(st.session_state.stage_mapping)} Mapping")
    st.markdown(f"{get_status_icon(st.session_state.stage_drafting)} Drafting")

if not os.getenv("GROQ_API_KEY"):
    st.sidebar.warning("WARNING: GROQ_API_KEY missing from environment.")

# ==========================================================
# PIPELINE EXECUTION LOGIC
# ==========================================================
if run_triggered:
    if not st.session_state.profile:
        st.error("Operation Aborted: Please upload a valid Company Profile JSON.")
    else:
        st.session_state.stage_inference = "Pending"
        st.session_state.stage_mapping = "Pending"
        st.session_state.stage_drafting = "Pending"

        try:
            with st.spinner("Executing Pipeline..."):
                # Inference
                st.session_state.stage_inference = "In-Progress"
                analysis_obj = analyze_company(st.session_state.profile)
                st.session_state.analysis = analysis_obj
                st.session_state.stage_inference = "Complete"

                # Mapping
                st.session_state.stage_mapping = "In-Progress"
                mapping_obj = map_services(analysis_obj)
                st.session_state.mapping = mapping_obj
                st.session_state.stage_mapping = "Complete"

                # Drafting
                st.session_state.stage_drafting = "In-Progress"
                pitch_obj = draft_pitches(st.session_state.profile, mapping_obj, tone_level=selected_val)
                st.session_state.pitches = pitch_obj
                st.session_state.stage_drafting = "Complete"

            st.rerun()

        except Exception as e:
            if st.session_state.stage_inference == "In-Progress":
                st.session_state.stage_inference = "Failed"
            elif st.session_state.stage_mapping == "In-Progress":
                st.session_state.stage_mapping = "Failed"
            elif st.session_state.stage_drafting == "In-Progress":
                st.session_state.stage_drafting = "Failed"
            
            st.error(f"Pipeline Interrupted: {e}")

# ==========================================================
# MAIN INTERFACE
# ==========================================================
if not st.session_state.profile:
    st.title("Enterprise Outreach Console")
    st.info("System Ready. Upload a company profile JSON to begin.")
else:
    profile = st.session_state.profile
    st.title(f"Target: {getattr(profile, 'company_name', 'Unknown Company')}")
    st.write("---")

    # ==========================================
    # SECTION 1: Company Overview
    # ==========================================
    st.markdown("### 📄 Company Overview")
    col1, col2 = st.columns([4, 2])
    
    with col1:
        st.markdown(f"**Company Name:** {getattr(profile, 'company_name', 'N/A')}")
        st.markdown(f"**Industry:** {getattr(profile, 'industry', 'N/A') or 'N/A'}")
        st.markdown(f"**Scale:** {getattr(profile, 'company_size', 'N/A') or 'N/A'}")
        
        summary = getattr(profile, 'business_summary', 'N/A')
        st.markdown(f"**Business Summary:** {summary or 'N/A'}")
        
    with col2:
        tech = getattr(profile, 'tech_stack', [])
        news = getattr(profile, 'recent_news', [])
        
        st.markdown(f"**Tech Stack:** {', '.join(tech) if tech else 'None identified'}")
        st.markdown(f"**Recent News:** {', '.join(news) if news else 'None available'}")

    st.write("---")

    # ==========================================
    # SECTION 2: Drafted Emails
    # ==========================================

    # Safely grab the core issue and recommended service to display below the emails
    mapping = st.session_state.mapping
    analysis = st.session_state.analysis
    
    recommended_service = "N/A"
    if mapping and hasattr(mapping, 'executive_decision'):
        recommended_service = getattr(mapping.executive_decision, 'recommended_service', 'N/A')
        
    core_issue = "N/A"
    if analysis:
        core_issue = getattr(analysis, 'underlying_theme', 'N/A')

    if st.session_state.pitches and hasattr(st.session_state.pitches, 'variants') and st.session_state.pitches.variants:
        st.markdown("### ✉️ Drafted Emails")
        st.markdown(f"**🎯 Target Issue:** {core_issue}")
        st.markdown(f"**🛠️ Service Pitched:** {recommended_service}")

        st.write("---")
        
        
        
        

        variants = st.session_state.pitches.variants
        tab_names = [getattr(var, 'angle_name', f"Variant {i+1}") for i, var in enumerate(variants)]
        tabs = st.tabs(tab_names)


        for idx, tab in enumerate(tabs):
            var = variants[idx]
            with tab:
                subj = getattr(var, 'subject_line', 'No subject provided')
                body = getattr(var, 'email_body', 'No body provided')
                rationale = getattr(var, 'why_this_angle', 'No rationale provided')
                
                st.markdown(f"**Subject:** `{subj}`")
                
                # Use a bordered container with markdown so the text wraps naturally
                with st.container(border=True):
                    # Replace single newlines with double spaces + newline for proper Markdown rendering
                    st.markdown(body.replace('\n', '  \n'))
                
                st.markdown(f"**Strategic Rationale:** {rationale}")
                
                st.markdown("---")

    # ==========================================
    # SECTION 3: Executive Recommendation
    # ==========================================
    mapping = st.session_state.mapping
    if mapping and hasattr(mapping, 'executive_decision') and mapping.executive_decision:
        st.markdown("### ⚡ Executive Recommendation")
        dec = mapping.executive_decision
        
        with st.container(border=True):
            rec_col1, rec_col2, rec_col3 = st.columns(3)
            with rec_col1:
                st.markdown(f"**Recommended Service:**  \n{getattr(dec, 'recommended_service', 'N/A')}")
            with rec_col2:
                st.markdown(f"**Priority:**  \n{getattr(dec, 'priority', 'N/A')}")
            with rec_col3:
                st.markdown(f"**Confidence:**  \n{getattr(dec, 'business_confidence', 'N/A')}")
            
            st.markdown("---")
            st.markdown(f"**Reason for Selection:**  \n{getattr(dec, 'primary_reason', 'N/A')}")
        
        st.write("---")

    # ==========================================
    # SECTION 4: Service Mapping (Collapsible)
    # ==========================================
    if mapping:
        with st.expander("🧭 Service Mapping", expanded=False):
            rec = getattr(mapping, 'primary_recommendation', None)
            
            if rec:
                st.markdown(f"**Recommended Service:** {getattr(rec, 'recommended_service', 'N/A')}")
                st.markdown(f"**Strategic Fit / What Changes:** {getattr(rec, 'what_changes', 'N/A')}")
                
                outcomes = getattr(rec, 'expected_business_outcomes', [])
                if outcomes:
                    st.markdown("**Expected Outcomes:**")
                    for out in outcomes:
                        st.markdown(f"- {out}")
                else:
                    st.markdown("*No specific business outcomes documented.*")
                
                st.markdown("---")
            
            cands = getattr(mapping, 'candidates', [])
            if cands:
                st.markdown("**Alternative Candidates Evaluated:**")
                for cand in cands:
                    with st.expander(getattr(cand, 'service_name', 'Unknown Candidate')):
                        st.markdown(f"**Category:** {getattr(cand, 'category', 'N/A')}")
                        st.markdown(f"**Why it fits:** {getattr(cand, 'why_it_fits', 'N/A')}")
                        st.markdown(f"**Value:** {getattr(cand, 'business_value', 'N/A')}/10 | **Complexity:** {getattr(cand, 'implementation_complexity', 'N/A')}/10")
            else:
                st.markdown("*No alternative candidates available.*")

    # ==========================================
    # SECTION 5: Inference Analysis (Collapsible)
    # ==========================================
    analysis = st.session_state.analysis
    if analysis:
        with st.expander("🧠 Inference Analysis", expanded=False):
            st.markdown(f"**Executive Summary:**  \n{getattr(analysis, 'executive_summary', 'N/A')}")
            st.markdown(f"**Underlying Theme:**  \n{getattr(analysis, 'underlying_theme', 'N/A')}")
            st.markdown(f"**Diagnostic Summary:**  \n{getattr(analysis, 'diagnostic_summary', 'N/A')}")
            
            st.markdown("---")
            
            problems = getattr(analysis, 'inferred_problems', [])
            if problems:
                for prob in problems:
                    with st.container(border=True):
                        st.markdown(f"#### {getattr(prob, 'title', 'Untitled Problem')}")
                        
                        p_col1, p_col2 = st.columns(2)
                        with p_col1:
                            st.markdown(f"**Severity:** {getattr(prob, 'severity', 'N/A')}/10")
                        with p_col2:
                            conf = getattr(prob, 'confidence', None)
                            conf_display = f"{conf:.2f}" if conf is not None else "N/A"
                            st.markdown(f"**Confidence:** {conf_display}")
                            
                        st.markdown(f"**Root Cause:** {getattr(prob, 'root_cause', 'N/A')}")
                        st.markdown(f"**Evidence:** {getattr(prob, 'evidence', 'N/A')}")
                        st.markdown(f"**Business Impact:** {getattr(prob, 'business_impact', 'N/A')}")
                        
                        depts = getattr(prob, 'affected_departments', [])
                        if depts:
                            st.markdown(f"**Affected Departments:** {', '.join(depts)}")
            else:
                st.markdown("*No specific problems inferred.*")