import os
from typing import Union, Dict, Any, List

from jd_understanding_agent.jd_analyzer import JDAnalyzer
from talent_search_agent.crawler import search_linkedin_profiles
from profile_analysis_agent.summary_profile import get_linkedin_profile_summary


def main(
    job_description: Union[str, os.PathLike],
    openai_api_key: str = None,
    model_name: str = "gpt-3.5-turbo",
    max_profiles: int = 30
) -> Dict[str, Any]:
    """
    Orchestrate the talent search pipeline:
    1. Analyze the job description to extract attributes.
    2. Search LinkedIn for profiles matching those attributes.
    3. Summarize each found LinkedIn profile.

    Args:
        job_description (Union[str, os.PathLike]): Path to a JD file (txt/pdf) or a JD string.
        openai_api_key (str, optional): OpenAI API key. Falls back to environment variable OPENAI_API_KEY.
        model_name (str, optional): Name of the OpenAI model to use for JD analysis.
        max_profiles (int, optional): Maximum number of LinkedIn profiles to retrieve.

    Returns:
        Dict[str, Any]: A mapping from LinkedIn profile URL to its summary dict.
    """
    # Determine API key
    api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key must be provided via argument or OPENAI_API_KEY environment variable.")

    # 1. Analyze the JD
    analyzer = JDAnalyzer(openai_api_key=api_key, model_name=model_name)
    attributes = analyzer.analyze_jd(job_description)

    # 2. Search LinkedIn profiles
    urls: List[str] = search_linkedin_profiles(attributes, max_profiles=max_profiles)

    # 3. Summarize each profile
    results: Dict[str, Any] = {}
    for url in urls:
        try:
            summary = get_linkedin_profile_summary(url)
            results[url] = summary
        except Exception as e:
            # Record error per profile
            results[url] = {"error": str(e)}
    return results