import json
from analyzer import JDAnalyzer


if __name__ == "__main__":
    # Initialize analyzer
    analyzer = JDAnalyzer(openai_api_key="your-openai-api-key")
    
    # Example job description
    sample_jd = """
    Senior Backend Developer - Remote
    
    We are seeking a skilled Senior Backend Developer to join our team. 
    
    Requirements:
    - Bachelor's degree in Computer Science or related field
    - 5+ years of experience in backend development
    - Strong proficiency in Python and Django framework
    - Experience with RESTful APIs and microservices
    - Knowledge of SQL databases (PostgreSQL preferred)
    - Experience with AWS cloud services
    - Docker and Kubernetes experience preferred
    - Strong problem-solving skills and ability to work independently
    
    Location: Remote (US candidates only)
    Must be authorized to work in the US without sponsorship.
    """
    
    # Analyze the job description
    result = analyzer.analyze_jd(sample_jd)
    print(json.dumps(result, indent=2)) 