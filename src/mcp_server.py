"""Model Context Protocol server implementation for DuckDuckGo search."""

import asyncio
from typing import Any, Dict, Optional

import structlog
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .search_handler import SearchHandler
from .utils import ResultFormatter

logger = structlog.get_logger(__name__)


class DuckDuckGoMCPServer:
    """MCP Server for DuckDuckGo search capabilities."""

    def __init__(
        self,
        search_rate_limit: int = 30,
        fetch_rate_limit: int = 20,
        max_results_default: int = 10,
        safe_mode_default: bool = True,
    ) -> None:
        """
        Initialize MCP server.

        Args:
            search_rate_limit: Maximum search requests per minute
            fetch_rate_limit: Maximum fetch requests per minute
            max_results_default: Default number of results
            safe_mode_default: Enable safe search by default
        """
        self.server = Server("duckduckgo-search")
        self.search_handler = SearchHandler(
            search_rate_limit=search_rate_limit,
            fetch_rate_limit=fetch_rate_limit,
            max_results_default=max_results_default,
            safe_mode_default=safe_mode_default,
        )
        self.formatter = ResultFormatter()

        # Register handlers
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register MCP tool handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="web_search",
                    description=(
                        "Search the web using DuckDuckGo. Returns a list of search results "
                        "with titles, URLs, and snippets. Best for finding current information, "
                        "researching topics, or discovering relevant web pages."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query string",
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return (default: 10)",
                                "minimum": 1,
                                "maximum": 50,
                            },
                            "region": {
                                "type": "string",
                                "description": (
                                    "Region code for search results "
                                    "(e.g., 'us-en', 'uk-en', 'wt-wt' for worldwide)"
                                ),
                                "default": "wt-wt",
                            },
                            "safe_search": {
                                "type": "boolean",
                                "description": "Enable safe search filtering",
                            },
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="fetch_page_content",
                    description=(
                        "Fetch and extract clean, readable content from a web page URL. "
                        "Removes ads, navigation, and other clutter, returning only the main "
                        "content optimized for reading and analysis."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL of the page to fetch and parse",
                                "format": "uri",
                            },
                        },
                        "required": ["url"],
                    },
                ),
                Tool(
                    name="suggest_related_searches",
                    description=(
                        "Get related search suggestions for a query. Useful for exploring "
                        "related topics, refining searches, or discovering new angles on a subject."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to get suggestions for",
                            },
                            "max_suggestions": {
                                "type": "integer",
                                "description": "Maximum number of suggestions to return (default: 5)",
                                "minimum": 1,
                                "maximum": 10,
                            },
                        },
                        "required": ["query"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls."""
            try:
                if name == "web_search":
                    return await self._handle_web_search(arguments)
                elif name == "fetch_page_content":
                    return await self._handle_fetch_content(arguments)
                elif name == "suggest_related_searches":
                    return await self._handle_suggestions(arguments)
                else:
                    error_msg = f"Unknown tool: {name}"
                    logger.error(error_msg, tool=name)
                    return [TextContent(type="text", text=error_msg)]

            except Exception as e:
                error_msg = self.formatter.format_error(e, f"Tool: {name}")
                logger.error("Tool call failed", tool=name, error=str(e))
                return [TextContent(type="text", text=error_msg)]

    async def _handle_web_search(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Handle web_search tool call."""
        query = arguments.get("query")
        if not query:
            logger.warning("Web search called without query parameter")
            return [TextContent(type="text", text="Error: 'query' parameter is required")]

        max_results = arguments.get("max_results")
        region = arguments.get("region", "wt-wt")
        safe_search = arguments.get("safe_search")

        result = await self.search_handler.web_search(
            query=query,
            max_results=max_results,
            region=region,
            safe_search=safe_search,
        )

        if result.get("success"):
            formatted = self.formatter.format_search_results(
                result.get("results", []), query
            )
            return [TextContent(type="text", text=formatted)]
        else:
            error_msg = f"Search failed: {result.get('error', 'Unknown error')}"
            logger.error("Web search failed", query=query, error=result.get('error'))
            return [TextContent(type="text", text=error_msg)]

    async def _handle_fetch_content(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Handle fetch_page_content tool call."""
        url = arguments.get("url")
        if not url:
            logger.warning("Fetch content called without url parameter")
            return [TextContent(type="text", text="Error: 'url' parameter is required")]

        result = await self.search_handler.fetch_page_content(url)

        if result.get("success"):
            content_data = result.get("data", {})
            formatted = self.formatter.format_page_content(content_data)
            # Truncate if too long
            formatted = self.formatter.truncate_content(formatted, max_length=8000)
            return [TextContent(type="text", text=formatted)]
        else:
            error_msg = f"Failed to fetch content: {result.get('error', 'Unknown error')}"
            logger.error("Fetch content failed", url=url, error=result.get('error'))
            return [TextContent(type="text", text=error_msg)]

    async def _handle_suggestions(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Handle suggest_related_searches tool call."""
        query = arguments.get("query")
        if not query:
            logger.warning("Suggestions called without query parameter")
            return [TextContent(type="text", text="Error: 'query' parameter is required")]

        max_suggestions = arguments.get("max_suggestions", 5)

        result = await self.search_handler.suggest_related_searches(query, max_suggestions)

        if result.get("success"):
            suggestions = result.get("suggestions", [])
            if suggestions:
                formatted = f"Related search suggestions for '{query}':\n\n"
                formatted += "\n".join(f"- {s}" for s in suggestions)
            else:
                formatted = f"No suggestions found for '{query}'"
            return [TextContent(type="text", text=formatted)]
        else:
            error_msg = f"Failed to get suggestions: {result.get('error', 'Unknown error')}"
            logger.error("Suggestions failed", query=query, error=result.get('error'))
            return [TextContent(type="text", text=error_msg)]

    async def run_stdio(self) -> None:
        """Run the MCP server using stdio transport."""
        try:
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options(),
                )
        except Exception as e:
            logger.error("MCP server error", error=str(e))
            raise
        finally:
            await self.cleanup()

    async def cleanup(self) -> None:
        """Clean up resources."""
        await self.search_handler.cleanup()


async def run_server(
    search_rate_limit: int = 30,
    fetch_rate_limit: int = 20,
    max_results_default: int = 10,
    safe_mode_default: bool = True,
) -> None:
    """
    Run the MCP server.

    Args:
        search_rate_limit: Maximum search requests per minute
        fetch_rate_limit: Maximum fetch requests per minute
        max_results_default: Default number of results
        safe_mode_default: Enable safe search by default
    """
    server = DuckDuckGoMCPServer(
        search_rate_limit=search_rate_limit,
        fetch_rate_limit=fetch_rate_limit,
        max_results_default=max_results_default,
        safe_mode_default=safe_mode_default,
    )
    await server.run_stdio()
