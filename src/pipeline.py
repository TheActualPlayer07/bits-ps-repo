import json
from src.ai_insights import generate_job_insights
from src.scraper import scrape_wwr_jobs, scrape_linkedin_jobs, scrape_internshala_jobs, scrape_naukri_jobs
from src.scoring import calculate_relevance_score
import concurrent.futures

def run_basic_pipeline(parsed_input, api_key=None, experience_level="Entry Level"):
    """
    Simulates the pipeline flow for Phase 7 (V2.0).
    Aggregates jobs from multiple sources, scores them based on skills and seniority,
    and attaches AI generated insights.
    """
    user_text = ""
    if parsed_input.get("success") and "data" in parsed_input and isinstance(parsed_input["data"], str):
        user_text = parsed_input["data"]

    # Run scrapers in parallel to speed up the process
    live_jobs = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_wwr = executor.submit(scrape_wwr_jobs)
        future_linkedin = executor.submit(scrape_linkedin_jobs, user_text if user_text else "software engineer")
        future_internshala = executor.submit(scrape_internshala_jobs)
        future_naukri = executor.submit(scrape_naukri_jobs)
        
        live_jobs.extend(future_wwr.result())
        live_jobs.extend(future_linkedin.result())
        live_jobs.extend(future_internshala.result())
        live_jobs.extend(future_naukri.result())
    
    matched_jobs = live_jobs
    
    if user_text:
        scored_jobs = []
        for job in live_jobs:
            score = calculate_relevance_score(job, user_text, experience_level)
            job["relevance_score"] = score
            if score > 0: # Filter out completely irrelevant jobs
                scored_jobs.append(job)
        
        # Sort jobs by relevance score descending
        scored_jobs.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        # Take Top 15 to avoid massive UI clutter and API costs
        if scored_jobs:
            matched_jobs = scored_jobs[:15]

    # Add AI insights if API key is present
    if api_key:
        for job in matched_jobs:
            insights = generate_job_insights(job, user_text, api_key)
            if insights:
                job["insights"] = insights

    return {
        "status": "success",
        "jobs": matched_jobs,
        "message": f"Found {len(matched_jobs)} top job matches from multiple sources."
    }
