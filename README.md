# LinkedIn Talent Search Agent

## Overview and Goal of this Project

The LinkedIn Talent Search Agent is an intelligent system designed to automate and streamline the process of identifying suitable candidates for job openings. It leverages large language models (LLMs) and web scraping techniques to analyze job descriptions, search for matching LinkedIn profiles, and then summarize these profiles for quick review.

The primary goals of this project are:
- To automate the initial screening of job applicants or potential candidates.
- To provide structured and summarized information about LinkedIn profiles based on job requirements.
- To reduce manual effort in talent acquisition and recruitment processes.

## Project Hierarchy Structure

The project is organized into several modules, each responsible for a specific part of the talent search pipeline:

```
linkedin-talent-search-agent/
  ├── config.env
  ├── README.md
  └── src/
      ├── jd_understanding_agent/
      │   ├── jd_analyzer.py
      │   ├── models.py
      │   └── utils.py
      ├── orchestrate.py
      ├── profile_analysis_agent/
      │   ├── profile_analyzer.py
      │   ├── scraper.py
      │   └── summary_profile.py
      └── talent_search_agent/
          └── crawler.py
```

### File Functions:

*   **`config.env`**: This file stores environment variables, including LinkedIn credentials and the OpenAI API key, which are essential for the agents to function.
*   **`README.md`**: This file provides an overview of the project, its structure, and instructions for setup and usage.

#### `src/` directory:

*   **`src/orchestrate.py`**: This is the main orchestration script that ties together all the agents. It takes a job description as input, uses the `jd_analyzer` to extract attributes, then uses the `crawler` to find LinkedIn profiles, and finally uses the `profile_analyzer` to summarize each found profile.
*   **`src/jd_understanding_agent/`**:
    *   **`jd_analyzer.py`**: This script contains the `JDAnalyzer` class, which uses an LLM (LangChain with OpenAI) to process job descriptions (either as strings or PDF files) and extract structured information like job title, required skills, experience, location, and search keywords.
    *   **`models.py`**: Defines the Pydantic data model (`JDAnalysisResult`) for the structured output of the `jd_analyzer`, ensuring data consistency and validation.
    *   **`utils.py`**: Provides utility functions such as `extract_text_from_pdf` (to read text from PDF files) and `preprocess_text` (to clean and normalize text before analysis).
*   **`src/profile_analysis_agent/`**:
    *   **`profile_analyzer.py`**: This module uses an LLM to transform raw scraped LinkedIn profile data into a structured Python dictionary, extracting information like name, skills, experience, and education.
    *   **`scraper.py`**: This script handles the web scraping of LinkedIn profiles using `Selenium` and `BeautifulSoup`. It logs into LinkedIn, navigates to profile URLs, and extracts raw data such as name, skills, experience, and education.
    *   **`summary_profile.py`**: This file acts as a pipeline orchestrator within the `profile_analysis_agent`, combining the `scraper` and `profile_analyzer` to provide a complete summary of a given LinkedIn profile URL.
*   **`src/talent_search_agent/`**:
    *   **`crawler.py`**: This script is responsible for searching LinkedIn profiles based on the attributes extracted from the job description. It uses Google search queries (e.g., `site:linkedin.com/in/`) to find relevant LinkedIn profile URLs.

## How to Use This Repo

Follow these steps to set up and run the LinkedIn Talent Search Agent:

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/linkedin-talent-search-agent.git
cd linkedin-talent-search-agent
```

### 2. Install Dependencies

Install the necessary Python packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create or update the `config.env` file in the root directory of your project with your LinkedIn username and password, and your OpenAI API key:

```
YOUR_LINKEDIN_USERNAME=your_linkedin_username
YOUR_LINKEDIN_PASSWORD=your_linkedin_password
OPENAI_API_KEY=your_openai_api_key
```

**Important**: Replace `your_linkedin_username`, `your_linkedin_password`, and `your_openai_api_key` with your actual credentials.

### 4. Run the Orchestrator

You can now run the main orchestration script, `orchestrate.py`, providing a job description as input. The job description can be either a plain text string or a path to a `.txt` or `.pdf` file.

**Example with a text file:**

First, create a `job_description.txt` file (or a `.pdf` file) in your project directory (e.g., in the root or a `data/` folder):

```
# Example job_description.txt content
Job Title: Senior Software Engineer
Location: Remote
Skills: Python, AWS, Docker, Kubernetes, Microservices
Experience: 5+ years
```

Then, run the orchestrator:

```bash
python src/orchestrate.py --job_description data/job_description.txt
```

**Example with a string:**

```bash
python src/orchestrate.py --job_description "We are looking for a Data Scientist with 3+ years of experience in machine learning and Python. Remote position."
```

The script will output the analyzed job description attributes and a list of found LinkedIn profiles with their summaries.
