# linkedin_searcher.py

from typing import Dict, List, Any, Set
from googlesearch import search  # pip install googlesearch-python

def google_search(query: str, num_results: int) -> List[str]:
    """
    Wrapper around googlesearch.search to fetch up to num_results URLs.
    """
    return list(search(query, num_results=num_results, lang="en"))


def search_linkedin_profiles(
    attributes: Dict[str, Any],
    max_profiles: int = 20
) -> List[str]:
    """
    Search LinkedIn profiles based on job attributes.

    Args:
        attributes: Dict with keys including:
            - title (str)
            - location (str)
            - skills (List[str])
            - search_keywords (List[str])
        max_profiles: Max number of profile URLs to return.

    Returns:
        List of up to max_profiles unique LinkedIn profile URLs.
    """
    profiles: Set[str] = set()

    title = attributes.get("title", "")
    location = attributes.get("location", "")
    skills = attributes.get("skills", [])
    keywords = attributes.get("search_keywords", [])

    # Build a list of query terms to try
    query_terms = []
    if keywords:
        query_terms.extend(keywords)
    else:
        # fallback to title + top 3 skills
        query_terms.append(title)
        query_terms.extend(skills[:3])

    for term in query_terms:
        if len(profiles) >= max_profiles:
            break

        # e.g. "site:linkedin.com/in/ Data Scientist San Francisco, CA"
        query = f"site:linkedin.com/in/ {term} {location}".strip()
        results = google_search(query, num_results=max_profiles)

        for url in results:
            # normalize and filter
            if "linkedin.com/in/" in url:
                clean = url.split("?")[0].rstrip("/")
                profiles.add(clean)
            if len(profiles) >= max_profiles:
                break

    return list(profiles)


if __name__ == "__main__":
    # --- Example input dict from your JDAnalyzer ---
    example_attributes = {
        "title": "AI Engineer",
        "minimum_degree": "Bachelor",
        "location": "San Francisco, CA",
        "skills": ["python", "machine learning", "sql", "pandas"],
        "experience": 3,
        "search_keywords": ["Data Scientist", "Machine Learning Engineer"],
        "workright_requirement": "None"
    }

    # --- Test the search function (limit to 3 for testing) ---
    test_results = search_linkedin_profiles(example_attributes, max_profiles=3)
    print("Found LinkedIn profiles:")
    for url in test_results:
        print(" -", url)
