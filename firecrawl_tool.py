from typing import Optional, List, Dict, Any
import logging
from agno.tools.toolkit import Toolkit
from firecrawl import FirecrawlApp

# Configure logging
logger = logging.getLogger(__name__)


class FirecrawlTools(Toolkit):
    """Firecrawl tools for web search and scraping"""
    
    def __init__(self, api_key: str):
        super().__init__(name="firecrawl_tools")
        self.app = FirecrawlApp(api_key=api_key)
        self.register(self.search)
        self.register(self.scrape)
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search the web using Firecrawl search API
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            
        Returns:
            List of search results with scraped content
        """
        logger.info(f"[TOOL CALL] Firecrawl search - Query: '{query}', Limit: {limit}")
        try:
            results = self.app.search(query, limit=limit)
            if hasattr(results, 'data'):
                logger.info(f"[TOOL RESPONSE] Found {len(results.data)} search results")
                for i, result in enumerate(results.data):
                    logger.info(f"  Result {i+1}: {result.get('url', 'No URL')}")
                return results.data
            logger.warning("[TOOL RESPONSE] No results found")
            return []
        except Exception as e:
            error_msg = str(e)
            logger.error(f"[TOOL ERROR] Search error: {error_msg}")
            
            # Return error information instead of empty list
            return [{
                "error": True,
                "message": error_msg,
                "type": "search_error"
            }]
    
    def scrape(self, url: str) -> Dict[str, Any]:
        """
        Scrape a specific URL using Firecrawl
        
        Args:
            url: The URL to scrape
            formats: List of formats to return (markdown, html, links, etc.)
            
        Returns:
            Scraped content in requested formats
        """
        # Force the format to markdown only, ignoring any external input
        formats = ["markdown"]

        logger.info(f"[TOOL CALL] Firecrawl scrape - URL: '{url}', Formats: {formats}")
        try:
            result = self.app.scrape_url(url, formats=formats)
            logger.info(f"[TOOL RESPONSE] Successfully scraped {url}")
            if 'markdown' in result:
                logger.info(f"  Content length: {len(result['markdown'])} characters")
            return result
        except Exception as e:
            error_msg = str(e)
            logger.error(f"[TOOL ERROR] Scrape error: {error_msg}")
            
            # Return error information instead of empty dict
            return {
                "error": True,
                "message": error_msg,
                "type": "scrape_error"
            }
    