"""DuckDuckGo search handler with rate limiting and error handling."""

import asyncio
from typing import Any, Dict, List, Optional

import structlog
from ddgs import DDGS

from .utils import RateLimiter, ContentParser, ResultFormatter

logger = structlog.get_logger(__name__)


class SearchHandler:
    """Handle DuckDuckGo search operations with rate limiting."""

    def __init__(
        self,
        search_rate_limit: int = 30,
        fetch_rate_limit: int = 20,
        max_results_default: int = 10,
        safe_mode_default: bool = True,
    ) -> None:
        """
        Initialize search handler.

        Args:
            search_rate_limit: Maximum search requests per minute
            fetch_rate_limit: Maximum fetch requests per minute
            max_results_default: Default number of results to return
            safe_mode_default: Enable safe search by default
        """
        self.max_results_default = max_results_default
        self.safe_mode_default = safe_mode_default

        # Initialize rate limiters
        self.search_limiter = RateLimiter(search_rate_limit)
        self.fetch_limiter = RateLimiter(fetch_rate_limit)

        # Initialize content parser
        self.content_parser = ContentParser()

        # Initialize result formatter
        self.formatter = ResultFormatter()

    async def web_search(
        self,
        query: str,
        max_results: Optional[int] = None,
        region: str = "wt-wt",
        safe_search: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Perform web search using DuckDuckGo.

        Args:
            query: Search query string
            max_results: Maximum number of results (uses default if None)
            region: Region code (e.g., 'us-en', 'uk-en', 'wt-wt' for worldwide)
            safe_search: Enable safe search (uses default if None)

        Returns:
            Dictionary containing search results and metadata

        Raises:
            Exception: If search fails after retries
        """
        # Apply rate limiting
        await self.search_limiter.acquire()

        # Use defaults if not specified
        max_results = max_results or self.max_results_default
        safe_search = safe_search if safe_search is not None else self.safe_mode_default

        try:
            # Run sync DDGS in thread pool
            results = await asyncio.to_thread(
                self._search_sync, query, max_results, region, safe_search
            )

            # Clean URLs in results
            for result in results:
                if "url" in result:
                    result["url"] = self.content_parser.clean_url(result["url"])

            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results),
                "region": region,
                "safe_search": safe_search,
            }

        except Exception as e:
            logger.error("Web search failed", query=query, error=str(e))
            return {
                "success": False,
                "query": query,
                "error": str(e),
                "error_type": type(e).__name__,
            }

    def _search_sync(
        self, query: str, max_results: int, region: str, safe_search: bool
    ) -> List[Dict[str, Any]]:
        """
        Synchronous search wrapper for DDGS.

        Args:
            query: Search query
            max_results: Maximum results
            region: Region code
            safe_search: Safe search enabled

        Returns:
            List of search results
        """
        with DDGS() as ddgs:
            safesearch = "on" if safe_search else "off"
            results = list(
                ddgs.text(
                    query,
                    region=region,
                    safesearch=safesearch,
                    max_results=max_results,
                )
            )
            return results

    async def fetch_page_content(self, url: str) -> Dict[str, Any]:
        """
        Fetch and parse content from a URL.

        Args:
            url: URL to fetch

        Returns:
            Dictionary containing page content and metadata

        Raises:
            Exception: If fetch fails
        """
        # Apply rate limiting
        await self.fetch_limiter.acquire()

        try:
            content_data = await self.content_parser.fetch_content(url)

            return {
                "success": True,
                "url": url,
                "data": content_data,
            }

        except Exception as e:
            logger.error("Failed to fetch page content", url=url, error=str(e))
            return {
                "success": False,
                "url": url,
                "error": str(e),
                "error_type": type(e).__name__,
            }

    async def suggest_related_searches(
        self, query: str, max_suggestions: int = 5
    ) -> Dict[str, Any]:
        """
        Get related search suggestions.

        Args:
            query: Original search query
            max_suggestions: Maximum number of suggestions

        Returns:
            Dictionary containing suggestions
        """
        # Apply rate limiting
        await self.search_limiter.acquire()

        try:
            # Run sync DDGS in thread pool
            suggestions = await asyncio.to_thread(
                self._suggestions_sync, query, max_suggestions
            )

            return {
                "success": True,
                "query": query,
                "suggestions": suggestions,
                "count": len(suggestions),
            }

        except Exception as e:
            logger.error("Failed to get suggestions", query=query, error=str(e))
            return {
                "success": False,
                "query": query,
                "error": str(e),
                "error_type": type(e).__name__,
            }

    def _suggestions_sync(self, query: str, max_suggestions: int) -> List[str]:
        """
        Synchronous suggestions wrapper for DDGS.

        Args:
            query: Search query
            max_suggestions: Maximum suggestions

        Returns:
            List of suggestion strings
        """
        # The new ddgs API doesn't have a dedicated suggestions method
        # We'll use text search and extract related terms from results
        suggestions = []
        try:
            with DDGS() as ddgs:
                # Get a few search results and extract related terms
                results = list(ddgs.text(f"{query} related", max_results=max_suggestions))
                for result in results:
                    title = result.get("title", "")
                    if title and title.lower() != query.lower():
                        # Create a suggestion based on the title
                        suggestions.append(title[:100])  # Limit length
        except Exception:
            # If suggestions fail, return empty list
            pass
        return suggestions[:max_suggestions]

    async def cleanup(self) -> None:
        """Clean up resources."""
        await self.content_parser.close()
