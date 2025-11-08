"""Tests for SearchHandler."""

import pytest
from src.search_handler import SearchHandler


@pytest.fixture
async def search_handler():
    """Create a SearchHandler instance for testing."""
    handler = SearchHandler(
        search_rate_limit=30,
        fetch_rate_limit=20,
        max_results_default=10,
        safe_mode_default=True,
    )
    yield handler
    await handler.cleanup()


@pytest.mark.asyncio
async def test_web_search_basic(search_handler):
    """Test basic web search functionality."""
    result = await search_handler.web_search(
        query="Python programming",
        max_results=5,
    )

    assert result is not None
    assert "success" in result
    if result["success"]:
        assert "results" in result
        assert "query" in result
        assert result["query"] == "Python programming"
        assert len(result["results"]) <= 5


@pytest.mark.asyncio
async def test_web_search_with_region(search_handler):
    """Test web search with region parameter."""
    result = await search_handler.web_search(
        query="weather",
        max_results=3,
        region="us-en",
    )

    assert result is not None
    assert "success" in result


@pytest.mark.asyncio
async def test_web_search_safe_mode(search_handler):
    """Test web search with safe mode."""
    result = await search_handler.web_search(
        query="test query",
        safe_search=True,
    )

    assert result is not None
    assert "success" in result
    if result["success"]:
        assert result.get("safe_search") is True


@pytest.mark.asyncio
async def test_suggest_related_searches(search_handler):
    """Test related search suggestions."""
    result = await search_handler.suggest_related_searches(
        query="machine learning",
        max_suggestions=5,
    )

    assert result is not None
    assert "success" in result
    if result["success"]:
        assert "suggestions" in result
        assert len(result["suggestions"]) <= 5


@pytest.mark.asyncio
async def test_rate_limiting(search_handler):
    """Test that rate limiting doesn't crash."""
    # Make multiple requests quickly
    for _ in range(3):
        result = await search_handler.web_search(
            query="test",
            max_results=1,
        )
        assert result is not None


@pytest.mark.asyncio
async def test_empty_query(search_handler):
    """Test handling of empty query."""
    result = await search_handler.web_search(
        query="",
        max_results=5,
    )

    # Should handle gracefully, either return error or empty results
    assert result is not None
    assert "success" in result
