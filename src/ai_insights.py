import os
import json
from openai import OpenAI

def generate_job_insights(job, user_profile, api_key):
    """
    Calls OpenAI API to generate insights about a job based on the user's profile.
    """
    if not api_key:
        return None

    try:
        client = OpenAI(api_key=api_key)
        
        prompt = f"""
You are an expert AI Career Advisor. Analyze the following job listing against the user's profile and provide insights.

Job Title: {job.get('title')}
Company: {job.get('company')}
Description: {job.get('description')}
Required Skills: {', '.join(job.get('skills_required', []))}

User Profile/Preferences:
{json.dumps(user_profile, indent=2)}

Provide your response in JSON format with exactly the following keys:
- "role_fit": A brief assessment (1-2 sentences) of how well the user fits this role.
- "skills_gained": What new skills the user could learn in this role.
- "work_culture": Likely work culture based on the description and company (if known).
- "career_path": Potential career advancement from this role.
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a JSON-generating career advisor. Only return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        insights = json.loads(response.choices[0].message.content)
        return insights
    except Exception as e:
        print(f"Error generating insights: {e}")
        return None
