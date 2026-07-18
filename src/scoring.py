def calculate_relevance_score(job, user_input, experience_level="Entry Level"):
    """
    Calculates a relevance score (0-100) based on how well the job matches the user input,
    factoring in the requested experience level and location (boosting India/Remote).
    """
    if not user_input or not isinstance(user_input, str):
        return 0
        
    score = 0
    user_keywords = [word.lower().strip(",.") for word in user_input.split() if len(word) > 2]
    
    if not user_keywords:
        return 0
        
    title = job.get('title', '').lower()
    description = job.get('description', '').lower()
    skills_required = [s.lower() for s in job.get('skills_required', [])]
    
    max_possible_score = len(user_keywords) * 15 # 15 points max per keyword
    
    for word in user_keywords:
        # Match in Title (High weight)
        if word in title:
            score += 10
        # Match in explicitly required skills (High weight)
        elif any(word in skill for skill in skills_required):
            score += 10
        # Match in description (Lower weight)
        elif word in description:
            score += 5
            
    # Normalize score to 0-100 based on keyword hits
    normalized_score = min(int((score / max_possible_score) * 100), 100) if max_possible_score > 0 else 0
    
    # Apply Experience / Seniority modifiers
    senior_keywords = ['senior', 'sr', 'lead', 'manager', 'director', 'principal', 'head', 'architect']
    entry_keywords = ['intern', 'internship', 'junior', 'jr', 'entry', 'trainee', 'fresher']
    
    is_senior_job = any(k in title for k in senior_keywords)
    is_entry_job = any(k in title for k in entry_keywords)
    
    seniority_penalty = 0
    if experience_level in ["Internship", "Entry Level"] and is_senior_job:
        seniority_penalty = 30
    elif experience_level in ["Senior", "Lead"] and is_entry_job:
        seniority_penalty = 30
        
    # Apply Location modifiers (Boosting India and Remote)
    location = job.get('location', '').lower()
    location_boost = 0
    if 'india' in location or 'remote' in location:
        location_boost = 15
        
    final_score = min(max(normalized_score + location_boost - seniority_penalty, 0), 100)
    return final_score
