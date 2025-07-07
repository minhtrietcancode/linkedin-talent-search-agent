from scraper import extract_linkedin_profile_data
from profile_analyzer import analyze_profile_data

def get_linkedin_profile_summary(url: str) -> dict:
    """
    Full pipeline: scrape, analyze, return structured dict.
    """
    raw = extract_linkedin_profile_data(url)
    return analyze_profile_data(raw)