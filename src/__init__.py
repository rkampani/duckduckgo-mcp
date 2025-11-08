"""DuckDuckGo MCP Server - A Model Context Protocol server for web search."""

__version__ = "1.0.0"

from .mcp_server import DuckDuckGoMCPServer, run_server
from .search_handler import SearchHandler

__all__ = ["DuckDuckGoMCPServer", "run_server", "SearchHandler"]
