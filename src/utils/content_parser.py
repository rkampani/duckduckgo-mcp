"""Content parsing and extraction utilities."""

import re
import ssl
from typing import Dict, Optional
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup
from readability import Document


class ContentParser:
    """Parse and extract clean content from web pages."""

    def __init__(self, timeout: int = 30) -> None:
        """
        Initialize content parser.

        Args:
            timeout: HTTP request timeout in seconds
        """
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            # Create SSL context that's more lenient (for development)
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            connector = aiohttp.TCPConnector(ssl=ssl_context)

            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; DuckDuckGoMCPServer/1.0)"
                },
                connector=connector,
            )
        return self._session

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def fetch_content(self, url: str) -> Dict[str, str]:
        """
        Fetch and parse content from a URL.

        Args:
            url: URL to fetch content from

        Returns:
            Dictionary containing title, content, and metadata

        Raises:
            aiohttp.ClientError: If the request fails
        """
        session = await self.get_session()

        async with session.get(url) as response:
            response.raise_for_status()
            html = await response.text()

        return self.parse_html(html, url)

    def parse_html(self, html: str, url: str = "") -> Dict[str, str]:
        """
        Parse HTML and extract clean content.

        Args:
            html: Raw HTML content
            url: Original URL (for reference)

        Returns:
            Dictionary with title, content, and metadata
        """
        # Use readability to extract main content
        doc = Document(html)
        title = doc.title()
        summary_html = doc.summary()

        # Parse with BeautifulSoup for further cleaning
        soup = BeautifulSoup(summary_html, "lxml")

        # Remove unwanted elements
        for element in soup.find_all(["script", "style", "nav", "footer", "aside"]):
            element.decompose()

        # Extract text
        text = soup.get_text(separator="\n", strip=True)

        # Clean up whitespace
        text = self._clean_text(text)

        # Extract metadata
        metadata = self._extract_metadata(html)

        return {
            "title": title,
            "content": text,
            "url": url,
            "domain": urlparse(url).netloc if url else "",
            "metadata": metadata,
        }

    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text content.

        Args:
            text: Raw text content

        Returns:
            Cleaned text
        """
        # Remove multiple consecutive newlines
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Remove excessive whitespace
        text = re.sub(r"[ \t]+", " ", text)

        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(line for line in lines if line)

        return text.strip()

    def _extract_metadata(self, html: str) -> Dict[str, str]:
        """
        Extract metadata from HTML.

        Args:
            html: Raw HTML content

        Returns:
            Dictionary of metadata
        """
        soup = BeautifulSoup(html, "lxml")
        metadata: Dict[str, str] = {}

        # Extract meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            metadata["description"] = str(meta_desc.get("content", ""))

        # Extract Open Graph data
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            metadata["og_title"] = str(og_title.get("content", ""))

        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            metadata["og_description"] = str(og_desc.get("content", ""))

        # Extract author
        author = soup.find("meta", attrs={"name": "author"})
        if author and author.get("content"):
            metadata["author"] = str(author.get("content", ""))

        return metadata

    @staticmethod
    def clean_url(url: str) -> str:
        """
        Clean tracking parameters from URL.

        Args:
            url: URL to clean

        Returns:
            Cleaned URL
        """
        # Remove common tracking parameters
        tracking_params = [
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "utm_term",
            "utm_content",
            "fbclid",
            "gclid",
            "msclkid",
        ]

        parsed = urlparse(url)
        if not parsed.query:
            return url

        # Filter out tracking parameters
        query_params = [
            param
            for param in parsed.query.split("&")
            if not any(param.startswith(f"{tp}=") for tp in tracking_params)
        ]

        # Reconstruct URL
        clean_query = "&".join(query_params)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}" + (
            f"?{clean_query}" if clean_query else ""
        )
