from typing import Dict, Any, List, Optional
from tavily import TavilyClient
from app.core.config import settings


class TavilySearchClient:
    def __init__(self):
        # Initialize Tavily client with API key
        self.client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        
    async def search(self, query: str, search_depth: str = "basic", max_results: int = 5) -> Dict[str, Any]:
        """
        Perform a web search using Tavily API
        
        Args:
            query: The search query string
            search_depth: 'basic' for faster results, 'advanced' for more comprehensive search
            max_results: Maximum number of search results to return
            
        Returns:
            Dictionary containing search results and metadata
        """
        try:
            # Check if API key is configured
            if not settings.TAVILY_API_KEY:
                print("Warning: TAVILY_API_KEY is not set in environment variables")
                return {"results": []}
                
            # Validate search depth
            if search_depth not in ["basic", "advanced"]:
                search_depth = "basic"
                
            print(f"Performing Tavily search for: '{query[:50]}...' (depth: {search_depth}, max_results: {max_results})")
                
            # Execute search
            response = self.client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results
            )
            
            result_count = len(response.get("results", []))
            print(f"Tavily search complete - found {result_count} results")
            
            return response
        except Exception as e:
            print(f"Error performing Tavily search: {str(e)}")
            # Return empty results rather than failing completely
            return {"results": []}
    async def search_with_context(self, 
                                 query: str,
                                 context: str, 
                                 search_depth: str = "basic", 
                                 max_results: int = 5) -> Dict[str, Any]:
        """
        Perform a web search with additional context using Tavily API
        
        Args:
            query: The search query string
            context: Additional context to help guide the search
            search_depth: 'basic' for faster results, 'advanced' for more comprehensive search
            max_results: Maximum number of search results to return
            
        Returns:
            Dictionary containing search results and metadata
        """
        try:
            # Combine query with context
            enhanced_query = f"{query} {context}"
            
            # Execute search
            return await self.search(enhanced_query, search_depth, max_results)
        except Exception as e:
            print(f"Error performing Tavily search with context: {str(e)}")
            # Return empty results rather than failing completely
            return {"results": []}
    
    async def extract_resource_info(self, search_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Extract clean, formatted resources from Tavily search results
        
        Args:
            search_results: The Tavily search results dictionary
            
        Returns:
            List of resources with title, url, and snippet
        """
        resources = []
        
        try:
            if "results" in search_results:
                for result in search_results["results"]:
                    resource = {
                        "title": result.get("title", "Untitled Resource"),
                        "url": result.get("url", ""),
                        "snippet": result.get("content", "No description available")[:200] + "..."
                    }
                    resources.append(resource)
                    
            return resources
        except Exception as e:
            print(f"Error extracting resource information: {str(e)}")
            return []
