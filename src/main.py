"""Main entry point for DuckDuckGo MCP Server Actor."""

import asyncio
import logging
import os
import sys
from typing import Any, Dict

import structlog

from .mcp_server import run_server

# Determine log level from environment (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL = os.getenv("MCP_LOG_LEVEL", "INFO").upper()
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
    is_apify = bool(os.getenv("APIFY_IS_AT_HOME") or os.getenv("APIFY_TOKEN"))
    logger.debug("Environment check", is_apify=is_apify,
                 apify_at_home=os.getenv("APIFY_IS_AT_HOME"),
                 has_token=bool(os.getenv("APIFY_TOKEN")))
    return is_apify


async def main() -> None:
    """Main entry point for the MCP Server (works both locally and on Apify)."""

    logger.debug("Starting main()",
                 python_version=sys.version,
                 log_level=LOG_LEVEL)

    # Determine if we're running in Apify or standalone mode
    use_apify = is_apify_environment()

    logger.info("Execution mode determined", mode="apify" if use_apify else "local")

    if use_apify:
        # Running on Apify platform - use Actor context
        from apify import Actor

        async with Actor:
            # Get input configuration from Apify
            actor_input: Dict[str, Any] = await Actor.get_input() or {}
            logger.debug("Actor input received", actor_input=actor_input)

            # Extract configuration
            mode = actor_input.get("mode", "stdio")
            search_rate_limit = actor_input.get("searchRateLimit", 30)
            fetch_rate_limit = actor_input.get("fetchRateLimit", 20)
            max_results_default = actor_input.get("maxResultsDefault", 10)
            safe_mode_default = actor_input.get("safeModeDefault", True)
            enable_logging = actor_input.get("enableLogging", True)

            logger.debug("Configuration extracted",
                        mode=mode,
                        search_rate_limit=search_rate_limit,
                        fetch_rate_limit=fetch_rate_limit,
                        max_results_default=max_results_default,
                        safe_mode_default=safe_mode_default,
                        enable_logging=enable_logging)

            # Configure logging level
            if not enable_logging:
                structlog.configure(
                    wrapper_class=structlog.make_filtering_bound_logger(logging.WARNING),
                )

            logger.info(
                "Starting DuckDuckGo MCP Server Actor (Apify mode)",
                mode=mode,
                search_rate_limit=search_rate_limit,
                fetch_rate_limit=fetch_rate_limit,
            )

            try:
                if mode == "stdio":
                    # Run MCP server in stdio mode
                    logger.info("Running in stdio mode")
                    await run_server(
                        search_rate_limit=search_rate_limit,
                        fetch_rate_limit=fetch_rate_limit,
                        max_results_default=max_results_default,
                        safe_mode_default=safe_mode_default,
                    )
                elif mode == "http":
                    # HTTP mode not yet implemented
                    logger.error("HTTP mode not yet implemented")
                    raise NotImplementedError("HTTP mode is not yet implemented")
                else:
                    logger.error("Invalid mode specified", mode=mode)
                    raise ValueError(f"Invalid mode: {mode}. Must be 'stdio' or 'http'")

            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down")
            except Exception as e:
                logger.error("Fatal error", error=str(e), exc_info=True)
                raise
            finally:
                logger.info("DuckDuckGo MCP Server Actor stopped")
    else:
        # Running locally (e.g., in Claude Desktop) - no Actor context needed
        # Use default configuration
        mode = "stdio"
        search_rate_limit = 30
        fetch_rate_limit = 20
        max_results_default = 10
        safe_mode_default = True

        logger.debug("Using default local configuration",
                    mode=mode,
                    search_rate_limit=search_rate_limit,
                    fetch_rate_limit=fetch_rate_limit,
                    max_results_default=max_results_default,
                    safe_mode_default=safe_mode_default)

        logger.info(
            "Starting DuckDuckGo MCP Server (Local mode)",
            mode=mode,
            search_rate_limit=search_rate_limit,
            fetch_rate_limit=fetch_rate_limit,
        )

        try:
            # Run MCP server in stdio mode
            logger.info("Running in stdio mode")
            await run_server(
                search_rate_limit=search_rate_limit,
                fetch_rate_limit=fetch_rate_limit,
                max_results_default=max_results_default,
                safe_mode_default=safe_mode_default,
            )

        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down")
        except Exception as e:
            logger.error("Fatal error", error=str(e), exc_info=True)
            raise
        finally:
            logger.info("DuckDuckGo MCP Server stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error("Fatal error in main", error=str(e))
        sys.exit(1)
