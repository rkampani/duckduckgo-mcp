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

### Using with Claude Desktop (Local Mode)

The server runs in **stdio mode** for local integration with Claude Desktop.

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "duckduckgo-search": {
      "command": "/path/to/duckduckgo-mcp/venv/bin/python",
      "args": [
        "/path/to/duckduckgo-mcp/run_mcp_server.py"
      ]
    }
  }
}
```

### Deploy to Apify (Remote HTTP Mode)

The Actor can run in **HTTP mode** for remote access via Apify's web infrastructure.

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

5. Configure the Actor with HTTP mode in Apify Console:
```json
{
  "mode": "http",
  "port": 3000,
  "searchRateLimit": 30,
  "fetchRateLimit": 20,
  "maxResultsDefault": 10,
  "safeModeDefault": true,
  "enableLogging": true
}
```

6. The Actor will run as a web server at:
```
https://YOUR_ACTOR_ID.apify.actor/
```

### Using the HTTP API

Once deployed in HTTP mode, you can interact with the MCP server via HTTP endpoints:

**Health Check:**
```bash
curl https://YOUR_ACTOR_ID.apify.actor/health
```

**List Available Tools:**
```bash
curl -X POST https://YOUR_ACTOR_ID.apify.actor/mcp/message \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'
```

**Perform Web Search:**
```bash
curl -X POST https://YOUR_ACTOR_ID.apify.actor/mcp/message \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "web_search",
      "arguments": {
        "query": "Python async programming",
        "max_results": 5
      }
    }
  }'
```

## Two Modes of Operation

This MCP server supports **two modes** to fit different use cases:

### 📍 stdio Mode (Local Integration)
- **Best for:** Claude Desktop, local MCP clients
- **Transport:** stdin/stdout (process-based)
- **Deployment:** Runs locally on your machine
- **Use case:** Personal use, development, testing
- **Configuration:** Set `mode: "stdio"`

### 🌐 HTTP Mode (Remote Access)
- **Best for:** Apify deployment, remote access, API integration
- **Transport:** HTTP/JSON-RPC
- **Deployment:** Runs as a web server (Apify Actor)
- **Use case:** Shared access, production deployment, integrations
- **Configuration:** Set `mode: "http"` with `port: 3000`

## Configuration

Configure the Actor through the input schema:

**For stdio mode (local):**
```json
{
  "mode": "stdio",
  "searchRateLimit": 30,
  "fetchRateLimit": 20,
  "maxResultsDefault": 10,
  "safeModeDefault": true,
  "enableLogging": true
}
```

**For HTTP mode (remote/Apify):**
```json
{
  "mode": "http",
  "host": "0.0.0.0",
  "port": 3000,
  "searchRateLimit": 30,
  "fetchRateLimit": 20,
  "maxResultsDefault": 10,
  "safeModeDefault": true,
  "enableLogging": true
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

## ⚠️ LEGAL DISCLAIMER & TERMS OF USE

**READ THIS CAREFULLY BEFORE USING THIS SOFTWARE**

### Critical Legal Notice

This software uses the unofficial `duckduckgo-search` Python library (ddgs) which scrapes DuckDuckGo's search results. **This activity violates DuckDuckGo's Terms of Service.**

### Terms of Service Violations

According to DuckDuckGo's Terms of Service:
- ❌ Automated access to search results is **prohibited**
- ❌ Scraping search data is **not permitted**
- ❌ Commercial use of scraped data **violates their ToS**
- ✅ DuckDuckGo offers official APIs, but they cost $500+/month for commercial use

### Official Position

- **NOT affiliated with DuckDuckGo** - This is an unofficial, third-party tool
- **NOT endorsed by DuckDuckGo** - They do not support or approve this usage
- **NOT for production use** - This violates their acceptable use policy

### Permitted Use

This software is provided **STRICTLY** for:
- ✅ Educational purposes and learning
- ✅ Personal research and experimentation
- ✅ Non-commercial academic study
- ✅ Local development and testing

### Prohibited Use

**DO NOT USE THIS SOFTWARE FOR:**
- ❌ Commercial applications or services
- ❌ Production deployments
- ❌ Paid products or services
- ❌ High-volume automated searches
- ❌ Any purpose that generates revenue
- ❌ Public-facing applications
- ❌ Business intelligence or data harvesting

### Legal Risks & Liability

By using this software, you acknowledge and accept that:

1. **You assume all legal risks** - The author bears no responsibility for your use
2. **You may face legal action** - DuckDuckGo may pursue violations of their ToS
3. **Your IP may be blocked** - Excessive usage will result in rate limiting or bans
4. **No warranty provided** - This software is provided "AS IS" without guarantees
5. **You are responsible** - Compliance with all applicable laws is your responsibility

### Privacy Notice

While this software:
- ✅ Does not track or store your queries locally
- ✅ Does not send data to third parties
- ✅ Uses DuckDuckGo's privacy-focused search engine

**Important**: DuckDuckGo will see your searches originating from your IP address, and their privacy policy applies to the search activity itself.

### Recommended Legal Alternatives

For commercial or production use, consider these legal alternatives:
- [Bing Search API](https://www.microsoft.com/en-us/bing/apis/bing-web-search-api) - Free tier: 1,000 queries/month
- [Google Custom Search API](https://developers.google.com/custom-search) - Free tier: 100 queries/day
- [Brave Search API](https://brave.com/search/api/) - Paid plans available
- [SerpAPI](https://serpapi.com/) - Legal scraping service with proper licensing
- [DuckDuckGo Official API](https://duckduckgo.com/api) - $500+/month for commercial search

### Author's Disclaimer

The author and contributors:
- Do not encourage violation of Terms of Service
- Provide this code for educational purposes only
- Assume no liability for misuse
- Recommend using legal alternatives for any commercial application

### License

This software is released under the MIT License, which means:
- ✅ You can use, modify, and distribute the code
- ❌ The license does NOT grant you rights to violate DuckDuckGo's ToS
- ❌ The MIT License provides NO warranty or liability coverage

**USE AT YOUR OWN RISK**

If you need commercial search capabilities, please use official, paid APIs from search providers.

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
