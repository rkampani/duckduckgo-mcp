#!/usr/bin/env python3
"""Simple entry point for running the DuckDuckGo MCP Server.

This script can be used directly without module path issues.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import and run
if __name__ == "__main__":
    import asyncio
    from src.main import main

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)
