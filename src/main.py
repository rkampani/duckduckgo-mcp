"""Main entry point for DuckDuckGo MCP Server Actor."""

import asyncio
import logging
import os
import sys
from typing import Any, Dict

import structlog

from .mcp_server import run_server

# Determine log level from environment (DEBUG, INFO, WARNING, ERROR)
# Default to WARNING - set MCP_LOG_LEVEL=DEBUG for troubleshooting
LOG_LEVEL = os.getenv("MCP_LOG_LEVEL", "WARNING").upper()
log_level_map = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}
selected_log_level = log_level_map.get(LOG_LEVEL, logging.INFO)

# Configure structured logging to stderr (stdout is reserved for MCP JSON-RPC)
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(selected_log_level),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),  # Output to stderr
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


def is_apify_environment() -> bool:
    """Check if running in Apify environment."""
    return bool(os.getenv("APIFY_IS_AT_HOME") or os.getenv("APIFY_TOKEN"))


async def main() -> None:
    """Main entry point for the MCP Server (works both locally and on Apify)."""
    # Determine if we're running in Apify or standalone mode
    use_apify = is_apify_environment()

    if use_apify:
        # Running on Apify platform - use Actor context
        from apify import Actor

        async with Actor:
            # Get input configuration from Apify
            actor_input: Dict[str, Any] = await Actor.get_input() or {}

            # Extract configuration
            mode = actor_input.get("mode", "stdio")
            host = actor_input.get("host", "0.0.0.0")
            port = actor_input.get("port", 3000)
            search_rate_limit = actor_input.get("searchRateLimit", 30)
            fetch_rate_limit = actor_input.get("fetchRateLimit", 20)
            max_results_default = actor_input.get("maxResultsDefault", 10)
            safe_mode_default = actor_input.get("safeModeDefault", True)
            enable_logging = actor_input.get("enableLogging", True)

            # Configure logging level
            if not enable_logging:
                structlog.configure(
                    wrapper_class=structlog.make_filtering_bound_logger(logging.WARNING),
                )

            try:
                # Run MCP server in specified mode
                await run_server(
                    mode=mode,
                    host=host,
                    port=port,
                    search_rate_limit=search_rate_limit,
                    fetch_rate_limit=fetch_rate_limit,
                    max_results_default=max_results_default,
                    safe_mode_default=safe_mode_default,
                )

            except KeyboardInterrupt:
                pass
            except Exception as e:
                logger.error("Fatal error", error=str(e), exc_info=True)
                raise
    else:
        # Running locally (e.g., in Claude Desktop) - no Actor context needed
        # Use default configuration
        search_rate_limit = 30
        fetch_rate_limit = 20
        max_results_default = 10
        safe_mode_default = True

        try:
            # Run MCP server in stdio mode
            await run_server(
                search_rate_limit=search_rate_limit,
                fetch_rate_limit=fetch_rate_limit,
                max_results_default=max_results_default,
                safe_mode_default=safe_mode_default,
            )

        except KeyboardInterrupt:
            pass
        except Exception as e:
            logger.error("Fatal error", error=str(e), exc_info=True)
            raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        logger.error("Fatal error in main", error=str(e))
        sys.exit(1)
