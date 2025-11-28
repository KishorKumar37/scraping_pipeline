from abc import ABC, abstractmethod
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup

from scraper.models import Page


class HtmlParser(ABC):
    @abstractmethod
    def process_page(
        self, url: str, response: httpx.Response
    ) -> tuple[Page | None, list[str]]:
        """Return a structured page plus outbound links extracted from HTML."""
        raise NotImplementedError

    @abstractmethod
    def _make_soup(self, response: httpx.Response) -> BeautifulSoup:
        """Build a BeautifulSoup tree from the HTTP response."""
        raise NotImplementedError

    @abstractmethod
    def _extract_content(self, soup: BeautifulSoup) -> str | None:
        """Extract textual content from the parsed document."""
        raise NotImplementedError

    @abstractmethod
    def _extract_links(self, soup: BeautifulSoup) -> list[str]:
        """Extract raw link targets from the parsed document."""
        raise NotImplementedError

    def _now_iso_utc(self) -> str:
        """Return the current time in ISO 8601 UTC."""
        return datetime.now(timezone.utc).isoformat()
