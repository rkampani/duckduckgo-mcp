"""Tests for RateLimiter."""

import asyncio
import pytest
from src.utils.rate_limiter import RateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_basic():
    """Test basic rate limiter functionality."""
    limiter = RateLimiter(max_requests=5, time_window=60)

    # Should be able to acquire 5 tokens
    for _ in range(5):
        result = await limiter.acquire(timeout=1.0)
        assert result is True


@pytest.mark.asyncio
async def test_rate_limiter_timeout():
    """Test rate limiter timeout behavior."""
    limiter = RateLimiter(max_requests=1, time_window=60)

    # First acquisition should succeed
    result = await limiter.acquire(timeout=1.0)
    assert result is True

    # Second should timeout quickly
    result = await limiter.acquire(timeout=0.1)
    assert result is False


@pytest.mark.asyncio
async def test_rate_limiter_refill():
    """Test that tokens refill over time."""
    limiter = RateLimiter(max_requests=2, time_window=1)

    # Use all tokens
    await limiter.acquire()
    await limiter.acquire()

    # Wait for refill
    await asyncio.sleep(0.6)

    # Should be able to acquire at least one more
    result = await limiter.acquire(timeout=0.5)
    assert result is True


@pytest.mark.asyncio
async def test_rate_limiter_reset():
    """Test rate limiter reset."""
    limiter = RateLimiter(max_requests=2, time_window=60)

    # Use all tokens
    await limiter.acquire()
    await limiter.acquire()

    # Reset
    limiter.reset()

    # Should be able to acquire again
    result = await limiter.acquire(timeout=0.1)
    assert result is True


def test_get_available_tokens():
    """Test getting available tokens."""
    limiter = RateLimiter(max_requests=10, time_window=60)

    available = limiter.get_available_tokens()
    assert available == 10
