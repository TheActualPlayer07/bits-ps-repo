import streamlit as st
import pandas as pd
from src.input_module import parse_excel_input, parse_text_input
from src.pipeline import run_basic_pipeline

def main():
    st.set_page_config(page_title="AI Job Discovery Agent", page_icon="🕵️‍♂️", layout="wide")
    
    st.title("🕵️‍♂️ AI Job Discovery Agent (V2.0)")
    st.markdown("Welcome! This agent helps you find the best job matches based on your profile and preferences.")
    
    st.sidebar.header("Settings")
    api_key = st.sidebar.text_input("OpenAI API Key (Phase 2 Insights)", type="password")
    
    st.sidebar.header("Experience Level")
    experience_level = st.sidebar.selectbox(
        "Select your desired experience level", 
        ["Internship", "Entry Level", "Mid Level", "Senior", "Lead"]
    )
    
    st.sidebar.header("User Input")
    input_method = st.sidebar.radio("Choose Input Method", ("Upload Excel file", "Direct Text / LinkedIn URL"))
    
    parsed_data = None
    
    if input_method == "Upload Excel file":
        st.subheader("Upload your Preferences/Skills Excel Sheet")
        uploaded_file = st.file_uploader("Choose an Excel file (.xlsx)", type=["xlsx"])
        
        if uploaded_file is not None:
            with st.spinner("Parsing Excel file..."):
                parsed_data = parse_excel_input(uploaded_file)
            
            if parsed_data.get("success"):
                st.success("File uploaded and parsed successfully!")
                with st.expander("View Extracted Data"):
                    st.write(parsed_data["data"])
            else:
                st.error(f"Error parsing file: {parsed_data.get('error')}")
                
    elif input_method == "Direct Text / LinkedIn URL":
        st.subheader("Enter your LinkedIn URL or a list of your skills")
        user_text = st.text_area("Input (e.g., Python, React, Data Analysis, India)")
        
        if user_text:
            parsed_data = parse_text_input(user_text)
            st.success("Text input received!")

    # Action Button to run pipeline
    st.divider()
    if st.button("🔍 Discover Jobs", type="primary"):
        if not parsed_data:
            st.warning("Please provide some input (Excel or Text) before discovering jobs.")
        else:
            with st.spinner("Scraping LinkedIn, Naukri, Internshala, and WWR... (this may take a moment)"):
                # Run the basic pipeline with live data
                result = run_basic_pipeline(parsed_data, api_key=api_key, experience_level=experience_level)
                
            if result["status"] == "success":
                st.subheader(result["message"])
                jobs = result["jobs"]
                
                if not jobs:
                    st.info("No matching jobs found on live job boards.")
                
                # Source Badges mapping
                source_badges = {
                    "LinkedIn": "🔵 LinkedIn",
                    "Internshala": "🟢 Internshala",
                    "Naukri": "🔴 Naukri",
                    "We Work Remotely": "🟡 WWR"
                }
                
                # Display jobs
                for i, job in enumerate(jobs):
                    with st.container():
                        badge = source_badges.get(job.get('source', ''), "⚪ Unknown")
                        st.markdown(f"### {i+1}. {job['title']} @ {job['company']}")
                        
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"🌍 **Location:** {job['location']} | 🏷️ **Source:** `{badge}`")
                            
                            # Format skills as markdown tags
                            skills_tags = " ".join([f"`{skill}`" for skill in job['skills_required']])
                            st.write(f"🛠️ **Skills:** {skills_tags if skills_tags else 'Not specified'}")
                            
                            st.write(f"📄 {job['description']}")
                            st.markdown(f"[🔗 Apply / View Job]({job.get('link', '#')})")
                            
                        with col2:
                            score = job.get('relevance_score')
                            if score is not None:
                                st.metric(label="🔥 Relevance Score", value=f"{score}/100")
                        
                        # Phase 2 & 5: Display AI Insights with clean UI
                        if "insights" in job:
                            with st.expander("🤖 View AI Job Insights"):
                                insights = job["insights"]
                                
                                st.success(f"**🎯 Role Fit:** {insights.get('role_fit', 'N/A')}")
                                
                                icol1, icol2 = st.columns(2)
                                with icol1:
                                    st.info(f"**📈 Skills to Gain:** {insights.get('skills_gained', 'N/A')}")
                                with icol2:
                                    st.info(f"**💼 Work Culture:** {insights.get('work_culture', 'N/A')}")
                                    
                                st.warning(f"**🚀 Career Path:** {insights.get('career_path', 'N/A')}")
                        
                        st.divider()

if __name__ == "__main__":
    main()
