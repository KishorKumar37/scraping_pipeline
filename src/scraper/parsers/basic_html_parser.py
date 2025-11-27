from bs4 import BeautifulSoup, Tag
import httpx
from scraper.models import Page
from scraper.parsers.interface import HtmlParser


class BasicHtmlParser(HtmlParser):
    def __init__(self) -> None:
        self._common_selectors: list[str] = [
            "header",
            ".site-header",
            ".main-header",
            ".header-box",
            "#header",
            "footer",
            ".site-footer",
            ".main-footer",
            "#footer",
            "tags-box",
        ]
        self._selectors_to_remove: list[str] = []
        self._first_page: bool = True

    def process_page(
        self, url: str, response: httpx.Response
    ) -> tuple[Page | None, list[str]]:
        soup: BeautifulSoup = self._make_soup(response)
        title: str = soup.title.text.strip() if soup.title else ""
        content: str | None = self._extract_content(soup)
        links: list[str] = self._extract_links(soup)

        page: Page | None = None
        if content:
            page = Page(title=title, url=url, text=content)

        return (page, links)

    def _make_soup(self, response: httpx.Response) -> BeautifulSoup:
        soup: BeautifulSoup = BeautifulSoup(
            markup=response.content, features="html.parser"
        )
        return soup

    def _extract_content(self, soup: BeautifulSoup) -> str | None:
        if self._first_page:
            self._learn_selectors_to_remove(soup)
            self._first_page = False

        for selector in self._selectors_to_remove:
            for element in soup.select(selector):
                element.decompose()

        body_tag: Tag | None = soup.find("body")
        if not body_tag:
            return None

        return body_tag.text

    def _learn_selectors_to_remove(self, soup: BeautifulSoup) -> None:
        for selector in self._common_selectors:
            if soup.select_one(selector):
                self._selectors_to_remove.append(selector)

        return None

    def _extract_links(self, soup: BeautifulSoup) -> list[str]:
        anchor_tags: list[Tag] = soup.find_all("a")
        links: list[str] = []
        for anchor_tag in anchor_tags:
            if not anchor_tag.get("href"):
                continue
            link: str = str(anchor_tag.get("href"))

            links.append(link)

        return links
