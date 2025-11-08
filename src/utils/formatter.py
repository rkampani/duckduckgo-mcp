"""Result formatting utilities for LLM consumption."""

import json
from datetime import datetime
from typing import Any, Dict, List


class ResultFormatter:
    """Format search results for optimal LLM consumption."""

    @staticmethod
    def format_search_results(results: List[Dict[str, Any]], query: str) -> str:
        """
        Format search results for LLM.

        Args:
            results: List of search results
            query: Original search query

        Returns:
            Formatted string optimized for LLM
        """
        if not results:
            return f"No results found for query: '{query}'"

        output_lines = [
            f"Search Results for: '{query}'",
            f"Found {len(results)} results",
            "",
        ]

        for idx, result in enumerate(results, 1):
            title = result.get("title", "No title")
            url = result.get("url", "")
            snippet = result.get("snippet", "No description available")

            output_lines.extend(
                [
                    f"[{idx}] {title}",
                    f"URL: {url}",
                    f"Description: {snippet}",
                    "",
                ]
            )

        return "\n".join(output_lines)

    @staticmethod
    def format_page_content(content_data: Dict[str, Any]) -> str:
        """
        Format page content for LLM.

        Args:
            content_data: Parsed content data

        Returns:
            Formatted content string
        """
        title = content_data.get("title", "Untitled")
        url = content_data.get("url", "")
        domain = content_data.get("domain", "")
        content = content_data.get("content", "")
        metadata = content_data.get("metadata", {})

        output_lines = [
            f"Page Title: {title}",
            f"URL: {url}",
            f"Domain: {domain}",
        ]

        if metadata.get("description"):
            output_lines.append(f"Description: {metadata['description']}")

        if metadata.get("author"):
            output_lines.append(f"Author: {metadata['author']}")

        output_lines.extend(["", "Content:", "=" * 80, content, "=" * 80])

        return "\n".join(output_lines)

    @staticmethod
    def format_error(error: Exception, context: str = "") -> str:
        """
        Format error message for LLM.

        Args:
            error: Exception that occurred
            context: Additional context about the error

        Returns:
            Formatted error message
        """
        error_type = type(error).__name__
        error_message = str(error)

        output_lines = [
            "An error occurred:",
            f"Type: {error_type}",
            f"Message: {error_message}",
        ]

        if context:
            output_lines.append(f"Context: {context}")

        return "\n".join(output_lines)

    @staticmethod
    def format_json(data: Any, indent: int = 2) -> str:
        """
        Format data as JSON.

        Args:
            data: Data to format
            indent: Indentation level

        Returns:
            JSON string
        """
        return json.dumps(data, indent=indent, ensure_ascii=False)

    @staticmethod
    def truncate_content(content: str, max_length: int = 5000) -> str:
        """
        Truncate content to maximum length.

        Args:
            content: Content to truncate
            max_length: Maximum length

        Returns:
            Truncated content
        """
        if len(content) <= max_length:
            return content

        return content[: max_length - 50] + "\n\n[Content truncated...]"

    @staticmethod
    def add_timestamp(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add timestamp to data.

        Args:
            data: Dictionary to add timestamp to

        Returns:
            Data with timestamp added
        """
        data["timestamp"] = datetime.utcnow().isoformat()
        return data
