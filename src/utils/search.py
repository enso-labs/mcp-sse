from tavily import TavilyClient
from src.config import Config
from typing import Literal
class Search:
    def __init__(self):
        self.client = TavilyClient(api_key=Config.TAVILY_API_KEY.value)

    def query(
        self, 
        query: str, 
        search_type: Literal["question", "context", None] = None,
        max_results: int = 5
    ) -> str:
        """
        Search the web
        
        Args:
            query: The search query
            search_type: Type of search to perform - "question" for context search,
                         "context" for context search, or "auto" to automatically detect
        """
        result = None
        if search_type == "question":
            result = self.client.qna_search(query, max_results=max_results)
        elif search_type == "context":
            result = self.client.get_search_context(query, max_results=max_results)
        else:
            result = self.client.search(query, max_results=max_results)
        return result
