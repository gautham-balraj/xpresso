import requests
from typing import List,Dict,Optional,Union

class TavilySearchAPI:

    """
    A wrapper for the Tavily API that provides search functionality.
    
    Attributes:
        __api_key (str): Private API key for authentication
        __base_url (str): Private base URL for the API endpoint
    """

    def __init__(self,api_key) -> None:
        self.__api_key = api_key
        self.__base_url = "https://api.tavily.com/search"

    def search(
        self,
        query: str,
        search_depth: str = "basic",
        topic: str = "general",
        days: Optional[int] = None,
        time_range: Optional[str] = None,
        max_results: int = 5,
        include_images: bool = False,
        include_image_descriptions: bool = False,
        include_answer: bool = False,
        include_raw_content: bool = False,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> Dict:
        """
         Args:
            query (str): The search query
            search_depth (str, optional): "basic" or "advanced". Defaults to "basic"
            topic (str, optional): "general" or "news". Defaults to "general"
            days (int, optional): Number of days back for news search. Defaults to None
            time_range (str, optional): "day"/"d", "week"/"w", "month"/"m", "year"/"y". Defaults to None
            max_results (int, optional): Maximum number of results. Defaults to 5
            include_images (bool, optional): Include image URLs. Defaults to False
            include_image_descriptions (bool, optional): Include image descriptions. Defaults to False
            include_answer (bool, optional): Include LLM-generated answer. Defaults to False
            include_raw_content (bool, optional): Include parsed HTML content. Defaults to False
            include_domains (List[str], optional): Domains to include. Defaults to None
            exclude_domains (List[str], optional): Domains to exclude. Defaults to None
        """

        if search_depth not in ["basic", "advanced"]:
            raise ValueError("search_depth must be 'basic' or 'advanced'")
        
        if topic not in ["general", "news"]:
            raise ValueError("topic must be 'general' or 'news'")
        
        if time_range and time_range.lower() not in ["day", "d", "week", "w", "month", "m", "year", "y"]:
            raise ValueError("Invalid time_range value")
        
        payload = {
            "api_key": self.__api_key,
            "query": query,
            "search_depth": search_depth,
            "topic": topic,
            "max_results": max_results,
            "include_images": include_images,
            "include_image_descriptions": include_image_descriptions,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content
        }
        # Add optional parameters if provided
        if days is not None and topic == "news":
            payload["days"] = days
            
        if time_range:
            payload["time_range"] = time_range
            
        if include_domains:
            payload["include_domains"] = include_domains
            
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains
        

        try:
            headers = {
                "Content-Type": "application/json"
            }
            response = requests.post(
                self.__base_url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"Tavily API request failed: {str(e)}")

    def format_llm(self, results: Dict) -> str:

        """
        Format search results for LLM consumption.
        
        Args:
            results (Dict): The search results from Tavily API
            
        Returns:
            str: Formatted string containing search results
            
        Raises:
            TypeError: If results is not a dictionary
        """
        
        if not isinstance(results, dict):
            raise TypeError("Results must be a dictionary")
        result = ""

        result += f"Query: {results['query']}\n"
        if 'answer' in results and results['answer']:
            result += "Generated Answer:\n"
            result += results['answer'] + "\n"
            result += "\n" + "="*50 + "\n"
        
        if 'results' in results:
            result += "Search Results:\n"
            filtered_results = [res for res in results['results']]
            for idx, res in enumerate(filtered_results, 1):
                result += f"\n{idx}. {res.get('title', 'No title')}\n"
                result += f"   URL: {res.get('url', 'No URL')}\n"
                result += f"   Relevance Score: {res.get('score', 'N/A')}\n"
                if 'published_date' in res:
                    result += f"   Published Date: {res['published_date']}\n"
                result += f"\n   Content: {res.get('content', 'No content')}\n"
                
        return result   