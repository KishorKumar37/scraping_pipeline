from __future__ import annotations

import logging
from typing import Any

from scraper.http.interface import HttpFetcher
from scraper.models import PageObject
from scraper.output.interface import OutputWriter
from scraper.parsers.interface import HtmlParser
from scraper.text_processing.interface import TextProcessor
from scraper.traversal.interface import TraversalStrategy
from scraper.utils.urls import (
    clean_and_normalize_link,
    extract_domain_root,
    is_same_domain,
    normalize_url,
)

logger = logging.getLogger(__name__)


class Crawler:
    def __init__(
        self,
        domain_url: str,
        start_url: str,
        traverser: TraversalStrategy,
        http_fetcher: HttpFetcher,
        html_parser: HtmlParser,
        text_processor: TextProcessor,
        output_writer: OutputWriter,
        max_pages: int | None,
        max_depth: int | None,
    ) -> None:
        """Wire together crawler dependencies and crawl limits."""
        self.domain_url = extract_domain_root(domain_url)
        self.start_url = normalize_url(start_url)
        if not is_same_domain(self.start_url, self.domain_url):
            raise ValueError("start_url must belong to domain_url")

        self._traverser = traverser
        self._http_fetcher = http_fetcher
        self._html_parser = html_parser
        self._text_processor = text_processor
        self._output_writer = output_writer

        self._max_pages = max_pages
        self._max_depth = max_depth

        self._seen: set[str] = set()
        self._cleanup_stack: list[tuple[str, Any]] = []
        return None

    async def __aenter__(self) -> "Crawler":
        """Enter async contexts for managed components."""
        self._cleanup_stack = []
        await self._enter_component("_http_fetcher")
        await self._enter_component("_output_writer")
        logger.info(
            "Crawler ready for domain %s (start: %s)", self.domain_url, self.start_url
        )
        return self

    async def _enter_component(self, attr_name: str) -> None:
        """Enter component context if supported and record cleanup action."""
        component: Any | None = getattr(self, attr_name, None)
        if component is None:
            return

        enter = getattr(component, "__aenter__", None)
        if callable(enter):
            entered_component = await enter()
            if entered_component is not None:
                setattr(self, attr_name, entered_component)
                component = entered_component
            self._cleanup_stack.append(("exit", component))
            logger.debug("Entered async context for %s", attr_name)
        elif callable(getattr(component, "aclose", None)):
            self._cleanup_stack.append(("close", component))
            logger.debug("Registered close callback for %s", attr_name)
        return None

    async def __aexit__(self, exc_type, exc, tb) -> None:
        """Close managed resources on exit."""
        await self.aclose()

    async def aclose(self) -> None:
        """Run cleanup callbacks collected during __aenter__."""
        if not hasattr(self, "_cleanup_stack"):
            return None

        while self._cleanup_stack:
            cleanup_type, component = self._cleanup_stack.pop()
            if cleanup_type == "exit":
                exit_method = getattr(component, "__aexit__", None)
                if callable(exit_method):
                    await exit_method(None, None, None)
                else:
                    close = getattr(component, "aclose", None)
                    if callable(close):
                        await close()
            elif cleanup_type == "close":
                close = getattr(component, "aclose", None)
                if callable(close):
                    await close()
        logger.info("Crawler resources closed")
        return None

    async def crawl(self) -> None:
        """Traverse URLs, fetch pages, and persist processed results."""
        self._seen.clear()
        pages_written = 0

        start_url = self.start_url
        self._seen.add(start_url)
        depth_by_url: dict[str, int] = {start_url: 0}
        self._traverser.push(start_url)
        logger.info("Starting crawl at %s", start_url)

        while not self._traverser.is_empty():
            if self._max_pages is not None and pages_written >= self._max_pages:
                logger.info("Stopping crawl after reaching max_pages=%s", self._max_pages)
                break

            current_url = self._traverser.pop()
            if current_url is None:
                break

            current_depth = depth_by_url.get(current_url, 0)
            if self._max_depth is not None and current_depth > self._max_depth:
                logger.debug(
                    "Skipping %s because depth %s exceeds max_depth %s",
                    current_url,
                    current_depth,
                    self._max_depth,
                )
                continue

            logger.debug("Fetching %s (depth=%s)", current_url, current_depth)
            response = await self._http_fetcher.get(current_url)
            if response is None:
                logger.debug("Fetch failed for %s; continuing", current_url)
                continue

            page, links = self._html_parser.process_page(current_url, response)
            if page is not None:
                processed_page, signals = self._text_processor.get_signals(page)
                page_object = PageObject(
                    **processed_page.model_dump(),
                    **signals.model_dump(),
                )
                await self._output_writer.write(page_object)
                pages_written += 1
                logger.info("Stored page #%s: %s", pages_written, current_url)

            if self._max_depth is not None and current_depth >= self._max_depth:
                continue

            for href in links:
                normalized = clean_and_normalize_link(
                    href=href, base_url=current_url, domain_root=self.domain_url
                )
                if normalized is None or normalized in self._seen:
                    logger.debug("Skipping invalid or seen link from %s -> %s", current_url, href)
                    continue

                next_depth = current_depth + 1
                if self._max_depth is not None and next_depth > self._max_depth:
                    continue

                self._seen.add(normalized)
                depth_by_url[normalized] = next_depth
                self._traverser.push(normalized)
                logger.debug("Queued %s (depth=%s)", normalized, next_depth)

        logger.info("Crawl finished; pages written: %s", pages_written)
        return None
