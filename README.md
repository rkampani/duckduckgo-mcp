# DuckDuckGo MCP Server

A Model Context Protocol (MCP) server that enables AI assistants and language models to perform real-time web searches using DuckDuckGo's privacy-focused search engine.


## Tools

### 1. `web_search`
Search the web using DuckDuckGo.

**Parameters:**
- `query` (string, required): The search query
- `max_results` (integer, optional): Maximum number of results (default: 10, max: 50)
- `region` (string, optional): Region code (e.g., 'us-en', 'uk-en', 'wt-wt' for worldwide)
- `safe_search` (boolean, optional): Enable safe search filtering

**Example:**
```json
{
  "query": "Python async programming",
  "max_results": 5,
  "region": "us-en",
  "safe_search": true
}
```

### 2. `fetch_page_content`
Fetch and extract clean content from a web page.

**Parameters:**
- `url` (string, required): The URL to fetch

**Example:**
```json
{
  "url": "https://example.com/article"
}
```

### 3. `suggest_related_searches`
Get related search suggestions.

**Parameters:**
- `query` (string, required): The search query
- `max_suggestions` (integer, optional): Maximum suggestions (default: 5, max: 10)

**Example:**
```json
{
  "query": "machine learning",
  "max_suggestions": 5
}
```

## Installation

### Prerequisites
- Python 3.10 or higher
- pip or uv package manager

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd duckduckgo-mcp
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the server:
```bash
python python run_mcp_server.py
```

### Using with Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "duckduckgo-search": {
      "command": "python",
      "args": [
        "-m",
        "src.main"
      ],
      "cwd": "/path/to/duckduckgo-mcp",
      "env": {}
    }
  }
}
```

### Deploy to Apify

1. Create an account at [Apify](https://apify.com)
2. Install Apify CLI:
```bash
npm install -g apify-cli
```

3. Login to Apify:
```bash
apify login
```

4. Deploy the Actor:
```bash
apify push
```

## Configuration

Configure the Actor through the input schema:

```json
{
  "mode": "stdio",
  "searchRateLimit": 30,
  "fetchRateLimit": 20,
  "maxResultsDefault": 10,
  "safeModeDefault": true,
  "enableLogging": true,
  "enableCaching": false,
  "cacheExpiryMinutes": 60
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `mode` | string | "stdio" | Server mode: "stdio" or "http" |
| `searchRateLimit` | integer | 30 | Max search requests per minute |
| `fetchRateLimit` | integer | 20 | Max fetch requests per minute |
| `maxResultsDefault` | integer | 10 | Default number of search results |
| `safeModeDefault` | boolean | true | Enable safe search by default |
| `enableLogging` | boolean | true | Enable detailed logging |
| `enableCaching` | boolean | false | Cache search results |
| `cacheExpiryMinutes` | integer | 60 | Cache expiry time |

## Architecture

```
duckduckgo-mcp/
├── .actor/
│   ├── actor.json           # Actor configuration
│   ├── input_schema.json    # Input validation schema
│   └── Dockerfile          # Container definition
├── src/
│   ├── __init__.py
│   ├── main.py             # Entry point
│   ├── mcp_server.py       # MCP protocol implementation
│   ├── search_handler.py   # DuckDuckGo search wrapper
│   └── utils/
│       ├── rate_limiter.py # Rate limiting logic
│       ├── content_parser.py # HTML parsing
│       └── formatter.py    # Result formatting
├── tests/
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
ruff check src/
```

### Type Checking

```bash
mypy src/
```

## Rate Limits

The server implements rate limiting to prevent abuse:

- **Search**: 30 requests per minute (configurable)
- **Fetch**: 20 requests per minute (configurable)

Rate limiting uses a token bucket algorithm that refills over time.

## Error Handling

The server provides comprehensive error handling:

- Network failures are caught and reported
- Rate limit violations are queued
- Invalid inputs are validated
- All errors return structured messages

## Use Cases

### For AI Developers
- Build chatbots with web search capabilities
- Create research assistants
- Develop fact-checking tools

### For Software Engineers
- Integrate search into applications
- Build custom search interfaces
- Create data collection pipelines

### For Researchers
- Combine AI reasoning with real-time data
- Perform automated research
- Analyze search trends

## Privacy & Terms

This Actor:
- Uses DuckDuckGo's privacy-focused search engine
- Does not track user queries
- Is for educational and research purposes
- Should respect DuckDuckGo's Terms of Service
- Is not affiliated with DuckDuckGo

**Important**: This tool is not intended for commercial use that violates DuckDuckGo's Terms of Service.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review the code examples

## Changelog

### Version 1.0.0
- Initial release
- Web search functionality
- Content fetching and parsing
- Search suggestions
- Rate limiting
- MCP protocol support
- Apify Actor integration

## Roadmap

Future enhancements:
- [ ] HTTP server mode
- [ ] News search
- [ ] Image search
- [ ] Video search
- [ ] Advanced caching
- [ ] Search history
- [ ] Analytics and metrics
- [ ] Multi-language support

## Credits

Built with:
- [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic
- [duckduckgo-search](https://github.com/deedy5/duckduckgo_search) library
- [Apify](https://apify.com) platform
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- [readability-lxml](https://github.com/buriy/python-readability) for content extraction
