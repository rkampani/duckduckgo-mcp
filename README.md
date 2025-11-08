# DuckDuckGo MCP Server

A Model Context Protocol (MCP) server that enables AI assistants to perform real-time web searches using DuckDuckGo.

## Features

- **Web Search**: Search the web with DuckDuckGo
- **Content Fetching**: Extract clean content from web pages
- **Search Suggestions**: Get related search suggestions
- **Dual Mode**: stdio (local) and HTTP (remote) support
- **Rate Limiting**: Built-in protection against abuse

## Quick Start

### Local Setup (Claude Desktop)

1. Install dependencies:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Configure Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "duckduckgo-search": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/run_mcp_server.py"]
    }
  }
}
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `mode` | "http" | "stdio" for local, "http" for remote |
| `port` | 3000 | HTTP port (http mode only) |
| `searchRateLimit` | 30 | Max searches per minute |
| `maxResultsDefault` | 10 | Default number of results |

## ⚠️ Legal Notice

This software uses an unofficial DuckDuckGo scraping library which **violates DuckDuckGo's Terms of Service**.

**For Educational Use Only:**
- ✅ Personal learning and research
- ✅ Local development and testing
- ❌ Commercial use or production deployments
- ❌ High-volume automated searches

**No Warranty**: Use at your own risk. The author assumes no liability.

**Commercial Alternatives:**
- [Bing Search API](https://www.microsoft.com/en-us/bing/apis/bing-web-search-api) - 1,000 free queries/month
- [Google Custom Search API](https://developers.google.com/custom-search) - 100 free queries/day
- [Brave Search API](https://brave.com/search/api/)

## License

