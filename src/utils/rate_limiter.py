"""Rate limiting implementation using token bucket algorithm."""

import asyncio
import time
from typing import Optional


class RateLimiter:
    """Token bucket rate limiter for API calls."""

    def __init__(self, max_requests: int, time_window: int = 60) -> None:
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum number of requests allowed in the time window
            time_window: Time window in seconds (default: 60 seconds)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.tokens = max_requests
        self.last_update = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self, timeout: Optional[float] = None) -> bool:
        """
        Acquire a token from the bucket.

        Args:
            timeout: Maximum time to wait for a token (None = wait indefinitely)

        Returns:
            True if token acquired, False if timeout reached
        """
        start_time = time.time()

        async with self._lock:
            while True:
                await self._refill_tokens()

                if self.tokens >= 1:
                    self.tokens -= 1
                    return True

                if timeout is not None and (time.time() - start_time) >= timeout:
                    return False

                # Wait for a short time before checking again
                await asyncio.sleep(0.1)

    async def _refill_tokens(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_update

        # Calculate how many tokens to add based on elapsed time
        tokens_to_add = (elapsed / self.time_window) * self.max_requests
        self.tokens = min(self.max_requests, self.tokens + tokens_to_add)
        self.last_update = now

    def get_available_tokens(self) -> float:
        """Get the current number of available tokens."""
        return self.tokens

    def reset(self) -> None:
        """Reset the rate limiter to full capacity."""
        self.tokens = self.max_requests
        self.last_update = time.time()
