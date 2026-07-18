import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import re
import urllib.parse

def scrape_wwr_jobs():
    """Scrapes We Work Remotely RSS feed."""
    url = "https://weworkremotely.com/categories/remote-programming-jobs.rss"
    headers = {"User-Agent": "Mozilla/5.0"}
    jobs_data = []
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        job_listings = root.findall('./channel/item')
        
        for idx, job in enumerate(job_listings):
            title_elem = job.find('title')
            link_elem = job.find('link')
            
            if title_elem is not None and title_elem.text:
                full_title = title_elem.text.strip()
                if ":" in full_title:
                    company, title = full_title.split(":", 1)
                    company = company.strip()
                    title = title.strip()
                else:
                    company = "Unknown"
                    title = full_title
                
                link = link_elem.text.strip() if (link_elem is not None and link_elem.text) else url
                keywords = title.replace(",", "").replace("-", " ").split()
                skills = [word for word in keywords if len(word) > 2]
                
                jobs_data.append({
                    "id": f"wwr_{idx}",
                    "title": title,
                    "company": company,
                    "location": "Remote",
                    "description": f"Remote job at {company}.",
                    "skills_required": skills,
                    "link": link,
                    "source": "We Work Remotely"
                })
            if len(jobs_data) >= 10: break
    except Exception as e:
        print(f"Failed to scrape WWR: {e}")
    return jobs_data

def scrape_linkedin_jobs(keywords="software engineer"):
    """Scrapes LinkedIn static jobs page for India."""
    query = urllib.parse.quote(keywords)
    url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location=India"
    headers = {"User-Agent": "Mozilla/5.0"}
    jobs_data = []
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            cards = soup.find_all('div', class_='base-search-card__info')
            for idx, card in enumerate(cards):
                title_elem = card.find('h3', class_='base-search-card__title')
                company_elem = card.find('h4', class_='base-search-card__subtitle')
                location_elem = card.find('span', class_='job-search-card__location')
                
                parent_a = card.parent.find('a', class_='base-card__full-link')
                
                if title_elem and company_elem:
                    title = title_elem.text.strip()
                    company = company_elem.text.strip()
                    location = location_elem.text.strip() if location_elem else "India"
                    link = parent_a['href'] if parent_a and 'href' in parent_a.attrs else url
                    
                    skill_keywords = title.replace(",", "").replace("-", " ").split()
                    skills = [w for w in skill_keywords if len(w) > 2]
                    
                    jobs_data.append({
                        "id": f"lin_{idx}",
                        "title": title,
                        "company": company,
                        "location": location,
                        "description": f"LinkedIn job at {company}.",
                        "skills_required": skills,
                        "link": link,
                        "source": "LinkedIn"
                    })
                if len(jobs_data) >= 10: break
    except Exception as e:
        print(f"Failed to scrape LinkedIn: {e}")
    return jobs_data

def scrape_internshala_jobs():
    """Scrapes Internshala for software engineering roles in India."""
    url = "https://internshala.com/internships/software-engineering-internships/"
    headers = {"User-Agent": "Mozilla/5.0"}
    jobs_data = []
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            meta_divs = soup.find_all('div', class_='internship_meta')
            for idx, meta in enumerate(meta_divs):
                title_elem = meta.find('a', class_='job-title-href')
                company_elem = meta.find('p', class_='company-name')
                location_elem = meta.find('a', class_='location_link')
                
                if title_elem and company_elem:
                    title = title_elem.text.strip()
                    company = company_elem.text.strip()
                    location = location_elem.text.strip() if location_elem else "India"
                    link = "https://internshala.com" + title_elem['href'] if 'href' in title_elem.attrs else url
                    
                    skill_keywords = title.replace(",", "").replace("-", " ").split()
                    skills = [w for w in skill_keywords if len(w) > 2]
                    
                    jobs_data.append({
                        "id": f"int_{idx}",
                        "title": title,
                        "company": company,
                        "location": location,
                        "description": f"Internship at {company}.",
                        "skills_required": skills,
                        "link": link,
                        "source": "Internshala"
                    })
                if len(jobs_data) >= 10: break
    except Exception as e:
        print(f"Failed to scrape Internshala: {e}")
    return jobs_data

def scrape_naukri_jobs():
    """Scrapes Naukri (basic attempt) or returns fallback if anti-bot blocks it."""
    url = "https://www.naukri.com/software-engineer-jobs-in-india"
    headers = {"User-Agent": "Mozilla/5.0"}
    jobs_data = []
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Naukri classes are highly dynamic, we attempt to find standard title tags
            title_tags = soup.find_all('a', class_='title')
            for idx, tag in enumerate(title_tags):
                title = tag.text.strip()
                company = "Naukri Listed Company" # Company name is usually in a sibling tag, hard to parse reliably without API
                link = tag['href'] if 'href' in tag.attrs else url
                
                skill_keywords = title.replace(",", "").replace("-", " ").split()
                skills = [w for w in skill_keywords if len(w) > 2]
                
                jobs_data.append({
                    "id": f"nkr_{idx}",
                    "title": title,
                    "company": company,
                    "location": "India",
                    "description": f"Naukri job listing.",
                    "skills_required": skills,
                    "link": link,
                    "source": "Naukri"
                })
                if len(jobs_data) >= 10: break
    except Exception as e:
        print(f"Failed to scrape Naukri: {e}")
    return jobs_data
