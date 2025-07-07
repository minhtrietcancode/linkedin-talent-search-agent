import re
import os
from typing import Dict, List, Union, Any
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from models import JDAnalysisResult
from utils import extract_text_from_pdf, preprocess_text


class JDAnalyzer:
    """
    Job Description Analyzer using LangChain
    Processes job descriptions (string or PDF) and extracts structured information
    """
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        """
        Initialize the JD Analyzer
        
        Args:
            model_name (str): LLM model to use (default: gpt-3.5-turbo)
        """
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model_name=model_name,
            temperature=0.1  # Low temperature for consistent extraction
        )
        
        # Setup output parser
        self.output_parser = PydanticOutputParser(pydantic_object=JDAnalysisResult)
        
        # Create the analysis prompt
        self.analysis_prompt = PromptTemplate(
            template="""
You are an expert HR analyst. Analyze the following job description and extract the required information.

Job Description:
{job_description}

Please extract the following information and return it in the specified JSON format:

1. **title**: The main job title/position name
2. **minimum_degree**: Education requirement (must be one of: "None", "Diploma", "Bachelor", "Master", "PhD")
3. **location**: Job location (city, state, country, or "Remote")
4. **skills**: List of technical skills, tools, technologies, and competencies required
5. **experience**: Minimum years of experience required (as integer, 0 if entry-level)
6. **search_keywords**: List of keywords that would be useful for searching candidates on LinkedIn
7. **workright_requirement**: Work authorization requirements ("None" if not specified, otherwise brief description)

Guidelines:
- For minimum_degree: If no specific degree is mentioned, use "None". Map certificates/diplomas to "Diploma".
- For experience: Extract numerical years. If range given (e.g., "3-5 years"), use the minimum.
- For skills: Include both technical and soft skills, programming languages, frameworks, tools.
- For search_keywords: Include job title variations, key technologies, and industry terms.
- For workright_requirement: Look for visa, citizenship, or authorization requirements.

{format_instructions}

Return only the JSON object with the extracted information.
""",
            input_variables=["job_description"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()}
        )
    
    def analyze_jd(self, job_description: Union[str, Path]) -> Dict[str, Any]:
        """
        Main method to analyze job description
        
        Args:
            job_description (Union[str, Path]): Either a string containing the JD 
                                              or a Path to a PDF file
            
        Returns:
            Dict[str, Any]: Structured analysis results
        """
        # Handle different input types
        if isinstance(job_description, (str, Path)) and Path(job_description).exists():
            # It's a file path
            if str(job_description).lower().endswith('.pdf'):
                jd_text = extract_text_from_pdf(job_description)
            else:
                # Assume it's a text file
                with open(job_description, 'r', encoding='utf-8') as file:
                    jd_text = file.read()
        else:
            # It's a string
            jd_text = str(job_description)
        
        # Preprocess the text
        jd_text = preprocess_text(jd_text)
        
        if not jd_text:
            raise ValueError("No text content found in job description")
        
        try:
            # Create the prompt
            formatted_prompt = self.analysis_prompt.format(job_description=jd_text)
            
            # Get LLM response
            messages = [
                SystemMessage(content="You are an expert HR analyst specializing in job description analysis."),
                HumanMessage(content=formatted_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Parse the response
            parsed_result = self.output_parser.parse(response.content)
            
            # Convert to dictionary
            result_dict = parsed_result.dict()
            
            # Post-process and validate
            result_dict = self._post_process_results(result_dict)
            
            return result_dict
            
        except Exception as e:
            # Fallback: try to parse manually if LLM parsing fails
            print(f"LLM parsing failed: {str(e)}")
            return self._fallback_analysis(jd_text)
    
    def _post_process_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post-process and validate results
        
        Args:
            results (Dict[str, Any]): Raw analysis results
            
        Returns:
            Dict[str, Any]: Processed and validated results
        """
        # Ensure skills are unique and non-empty
        if 'skills' in results:
            results['skills'] = list(set([skill.strip() for skill in results['skills'] if skill.strip()]))
        
        # Ensure search_keywords are unique and non-empty
        if 'search_keywords' in results:
            results['search_keywords'] = list(set([kw.strip() for kw in results['search_keywords'] if kw.strip()]))
        
        # Validate experience is non-negative
        if 'experience' in results:
            results['experience'] = max(0, results['experience'])
        
        # Ensure location is not empty
        if 'location' in results and not results['location']:
            results['location'] = "Not specified"
        
        # Ensure title is not empty
        if 'title' in results and not results['title']:
            results['title'] = "Not specified"
        
        return results
    
    def _fallback_analysis(self, jd_text: str) -> Dict[str, Any]:   
        """
        Fallback analysis using rule-based extraction
        
        Args:
            jd_text (str): Job description text
            
        Returns:
            Dict[str, Any]: Basic analysis results
        """
        # Basic fallback implementation
        results = {
            "title": "Not specified",
            "minimum_degree": "None",
            "location": "Not specified",
            "skills": [],
            "experience": 0,
            "search_keywords": [],
            "workright_requirement": "None"
        }
        
        # Simple keyword extraction for skills
        skill_keywords = [
            "python", "java", "javascript", "react", "angular", "vue", "node", "django", "flask",
            "sql", "mongodb", "postgresql", "mysql", "aws", "docker", "kubernetes", "git",
            "machine learning", "ai", "data science", "analytics", "tableau", "powerbi"
        ]
        
        jd_lower = jd_text.lower()
        found_skills = [skill for skill in skill_keywords if skill in jd_lower]
        results["skills"] = found_skills[:10]  # Limit to 10 skills
        
        # Extract experience years
        exp_match = re.search(r'(\d+)\s*(?:\+|\-|\s)*\s*years?\s*(?:of\s*)?experience', jd_lower)
        if exp_match:
            results["experience"] = int(exp_match.group(1))
        
        return results
    
    def batch_analyze(self, job_descriptions: List[Union[str, Path]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple job descriptions
        
        Args:
            job_descriptions (List[Union[str, Path]]): List of JDs or file paths
            
        Returns:
            List[Dict[str, Any]]: List of analysis results
        """
        results = []
        for jd in job_descriptions:
            try:
                result = self.analyze_jd(jd)
                results.append(result)
            except Exception as e:
                print(f"Error analyzing JD: {str(e)}")
                results.append(None)
        return results