import json
import time
import re
import os
from typing import List, Dict, Optional
import requests
from urllib.parse import urlparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImprovedTalentSearchAgent:
    def __init__(self, delay: float = 1.0, max_results_per_query: int = 10, use_serpapi: bool = False):
        """
        Initialize the Improved Talent Search Agent
        
        Args:
            delay: Delay between search queries (seconds)
            max_results_per_query: Maximum results per search query
            use_serpapi: Whether to use SerpAPI (requires API key)
        """
        self.delay = delay
        self.max_results_per_query = max_results_per_query
        self.use_serpapi = use_serpapi
        self.serpapi_key = os.getenv('SERPAPI_KEY')  # Get from environment variable
        
        self.linkedin_profile_pattern = re.compile(
            r'https?://(?:www\.)?linkedin\.com/in/([a-zA-Z0-9\-_]+)/?(?:\?.*)?'
        )
        
        # Session for reusing connections
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
    
    def search_linkedin_profiles(self, jd_analysis: Dict, max_total_results: int = 50) -> List[str]:
        """
        Search for LinkedIn profiles based on JD analysis
        
        Args:
            jd_analysis: Output from Agent 1 (JD Understanding Agent)
            max_total_results: Maximum total LinkedIn profiles to return
            
        Returns:
            List of unique LinkedIn profile URLs
        """
        logger.info("Starting LinkedIn profile search...")
        
        # Build search queries
        search_queries = self._build_optimized_search_queries(jd_analysis)
        
        all_linkedin_urls = set()
        
        for i, query in enumerate(search_queries, 1):
            if len(all_linkedin_urls) >= max_total_results:
                break
                
            logger.info(f"Query {i}/{len(search_queries)}: {query}")
            
            try:
                # Choose search method
                if self.use_serpapi and self.serpapi_key:
                    search_results = self._search_with_serpapi(query)
                else:
                    search_results = self._search_with_duckduckgo(query)
                
                # Extract LinkedIn URLs
                linkedin_urls = self._extract_linkedin_urls(search_results)
                all_linkedin_urls.update(linkedin_urls)
                
                logger.info(f"Found {len(linkedin_urls)} LinkedIn profiles (Total: {len(all_linkedin_urls)})")
                
                # Rate limiting
                time.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Search failed for query '{query}': {str(e)}")
                continue
        
        # Validate and return results
        result_urls = list(all_linkedin_urls)[:max_total_results]
        validated_urls = self._validate_linkedin_urls(result_urls)
        
        logger.info(f"Search completed. Found {len(validated_urls)} valid LinkedIn profiles")
        return validated_urls
    
    def _build_optimized_search_queries(self, jd_analysis: Dict) -> List[str]:
        """
        Build optimized search queries for better LinkedIn profile discovery
        """
        queries = []
        
        title = jd_analysis.get("title", "")
        location = jd_analysis.get("location", "")
        skills = jd_analysis.get("skills", [])
        
        # Strategy 1: Direct title search
        if title:
            queries.append(f'site:linkedin.com/in "{title}"')
            if location:
                queries.append(f'site:linkedin.com/in "{title}" "{location}"')
        
        # Strategy 2: Skills combination
        if len(skills) >= 2:
            top_skills = skills[:2]
            queries.append(f'site:linkedin.com/in "{top_skills[0]}" "{top_skills[1]}"')
            
            if location:
                queries.append(f'site:linkedin.com/in "{top_skills[0]}" "{top_skills[1]}" "{location}"')
        
        # Strategy 3: Title + main skill
        if title and skills:
            queries.append(f'site:linkedin.com/in "{title}" "{skills[0]}"')
        
        # Strategy 4: Broad search with location
        if location:
            queries.append(f'site:linkedin.com/in "{location}" developer')
            queries.append(f'site:linkedin.com/in "{location}" engineer')
        
        # Remove duplicates
        return list(dict.fromkeys(queries))[:4]  # Limit to 4 queries
    
    def _search_with_serpapi(self, query: str) -> List[str]:
        """
        Search using SerpAPI (more reliable but requires API key)
        """
        try:
            url = "https://serpapi.com/search"
            params = {
                "engine": "google",
                "q": query,
                "num": self.max_results_per_query,
                "api_key": self.serpapi_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            urls = []
            
            # Extract URLs from organic results
            for result in data.get("organic_results", []):
                if "link" in result:
                    urls.append(result["link"])
            
            return urls
            
        except Exception as e:
            logger.error(f"SerpAPI search failed: {str(e)}")
            return []
    
    def _search_with_duckduckgo(self, query: str) -> List[str]:
        """
        Search using DuckDuckGo (free alternative)
        """
        try:
            # DuckDuckGo search URL
            search_url = "https://duckduckgo.com/html/"
            params = {
                "q": query,
                "kl": "us-en"
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse results
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            urls = []
            # Find result links
            for link in soup.find_all('a', {'class': 'result__a'}):
                href = link.get('href')
                if href and 'linkedin.com' in href:
                    urls.append(href)
            
            return urls[:self.max_results_per_query]
            
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {str(e)}")
            return self._fallback_manual_search(query)
    
    def _fallback_manual_search(self, query: str) -> List[str]:
        """
        Fallback method using direct Google search
        """
        try:
            import urllib.parse
            from bs4 import BeautifulSoup
            
            # Use different Google domains to avoid blocking
            google_domains = [
                "https://www.google.com/search",
                "https://www.google.co.uk/search",
                "https://www.google.ca/search"
            ]
            
            encoded_query = urllib.parse.quote_plus(query)
            
            for domain in google_domains:
                try:
                    search_url = f"{domain}?q={encoded_query}&num={self.max_results_per_query}"
                    
                    response = self.session.get(search_url, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    urls = []
                    
                    # Extract URLs from search results
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if href.startswith('/url?q='):
                            actual_url = href.split('/url?q=')[1].split('&')[0]
                            actual_url = urllib.parse.unquote(actual_url)
                            if 'linkedin.com' in actual_url:
                                urls.append(actual_url)
                    
                    if urls:
                        logger.info(f"Fallback search found {len(urls)} URLs")
                        return urls[:self.max_results_per_query]
                        
                except Exception as e:
                    logger.warning(f"Failed with domain {domain}: {str(e)}")
                    continue
            
            return []
            
        except Exception as e:
            logger.error(f"All fallback methods failed: {str(e)}")
            return []
    
    def _extract_linkedin_urls(self, urls: List[str]) -> List[str]:
        """
        Extract and clean LinkedIn profile URLs
        """
        linkedin_urls = []
        
        for url in urls:
            match = self.linkedin_profile_pattern.search(url)
            if match:
                clean_url = self._clean_linkedin_url(url)
                if clean_url and self._is_valid_linkedin_profile_url(clean_url):
                    linkedin_urls.append(clean_url)
        
        return linkedin_urls
    
    def _clean_linkedin_url(self, url: str) -> Optional[str]:
        """
        Clean LinkedIn URL by removing unnecessary parameters
        """
        try:
            # Remove Google redirect if present
            if '/url?q=' in url:
                url = url.split('/url?q=')[1].split('&')[0]
                import urllib.parse
                url = urllib.parse.unquote(url)
            
            # Parse and clean URL
            parsed = urlparse(url)
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            clean_url = clean_url.rstrip('/')
            
            return clean_url
            
        except Exception:
            return None
    
    def _is_valid_linkedin_profile_url(self, url: str) -> bool:
        """
        Validate LinkedIn profile URL format
        """
        try:
            if not url.startswith(('http://', 'https://')):
                return False
            
            if 'linkedin.com' not in url or '/in/' not in url:
                return False
            
            profile_id = url.split('/in/')[-1]
            if not profile_id or len(profile_id) < 2:
                return False
            
            # Check for valid characters
            if not re.match(r'^[a-zA-Z0-9\-_]+$', profile_id):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _validate_linkedin_urls(self, urls: List[str]) -> List[str]:
        """
        Validate LinkedIn URLs
        """
        valid_urls = []
        
        for url in urls:
            if self._is_valid_linkedin_profile_url(url):
                valid_urls.append(url)
        
        return valid_urls
    
    def save_results(self, linkedin_urls: List[str], output_file: str = "linkedin_profiles.json"):
        """
        Save results to JSON file
        """
        try:
            results = {
                "total_profiles": len(linkedin_urls),
                "profiles": [
                    {
                        "url": url,
                        "profile_id": url.split('/in/')[-1]
                    }
                    for url in linkedin_urls
                ],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")

# Usage example
if __name__ == "__main__":
    sample_jd_analysis = {
        "title": "Backend Developer",
        "location": "Ho Chi Minh",
        "skills": ["Python", "Django", "REST API"],
        "experience": "2+ years"
    }
    
    # Initialize improved agent
    search_agent = ImprovedTalentSearchAgent(delay=2.0, max_results_per_query=10)
    
    # Search for profiles
    linkedin_profiles = search_agent.search_linkedin_profiles(
        jd_analysis=sample_jd_analysis,
        max_total_results=20
    )
    
    # Display results
    print(f"\nFound {len(linkedin_profiles)} LinkedIn profiles:")
    for i, profile in enumerate(linkedin_profiles, 1):
        print(f"{i}. {profile}")
    
    # Save results
    search_agent.save_results(linkedin_profiles)