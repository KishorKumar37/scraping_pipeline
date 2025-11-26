from abc import ABC, abstractmethod

import httpx
from bs4 import BeautifulSoup

from scraper.models import Page


class HtmlParser(ABC):
    @abstractmethod
    def process_page(
        self, url: str, response: httpx.Response
    ) -> tuple[Page | None, list[str]]:
        raise NotImplementedError

    @abstractmethod
    def _make_soup(self, response: httpx.Response) -> BeautifulSoup:
        raise NotImplementedError

    @abstractmethod
    def _extract_content(self, soup: BeautifulSoup) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def _extract_links(self, soup: BeautifulSoup) -> list[str]:
        raise NotImplementedError
