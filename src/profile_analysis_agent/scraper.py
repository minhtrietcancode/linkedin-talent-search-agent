import re
import time
from typing import Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def load_credentials(env_path: str = "config.env") -> Dict[str, str]:
    """
    Read first two lines from config.env as username and password.
    """
    with open(env_path, "r") as f:
        lines = f.read().splitlines()
    if len(lines) < 2:
        raise ValueError("config.env must contain at least two lines")
    return {"username": lines[0].strip(), "password": lines[1].strip()}

def extract_linkedin_profile_data(url: str) -> Dict[str, Any]:
    """
    Scrape basic profile fields from a LinkedIn profile.
    """
    # Validate URL
    if not re.match(r"^https://(www\.)?linkedin\.com/in/[A-Za-z0-9\-_%]+/?$", url):
        raise ValueError(f"Invalid LinkedIn profile URL: {url}")

    creds = load_credentials()
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    # Login if credentials provided
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)
    driver.find_element("id", "username").send_keys(creds["username"])
    driver.find_element("id", "password").send_keys(creds["password"])
    driver.find_element("xpath", '//button[@type="submit"]').click()
    time.sleep(2)

    # Fetch profile page
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    # Parse name
    name_tag = soup.select_one("h1.text-heading-xlarge")
    if not name_tag:
        raise ValueError("Failed to parse name")
    name = name_tag.get_text(strip=True)

    # Parse skills
    skills = [el.get_text(strip=True) for el in soup.select(".pv-skill-category-entity__name-text")]

    # Parse years of experience
    exp_match = soup.find(text=re.compile(r"\d+\+?\s+years"))
    exp_text = exp_match.strip() if exp_match else "0 years"

    # Parse education
    edu_entries = []
    for edu in soup.select(".pv-education-entity"):
        school = edu.select_one("h3.pv-entity__school-name")
        degree = edu.select_one(".pv-entity__degree-name .t-14")
        if school:
            edu_entries.append({
                "school": school.get_text(strip=True),
                "degree": degree.get_text(strip=True) if degree else ""
            })

    return {
        "raw_name": name,
        "raw_skills": skills,
        "raw_experience": exp_text,
        "raw_education": edu_entries
    }
