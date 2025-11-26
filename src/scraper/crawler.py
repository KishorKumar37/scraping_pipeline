from scraper.http.interface import HttpFetcher
from scraper.output.interface import OutputWriter
from scraper.parsers.interface import HtmlParser
from scraper.text_processing.interface import TextProcessor
from scraper.traversal.interface import TraversalStrategy


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
        max_pages: int,
        max_depth: int,
    ) -> None:
        self.domain_url = domain_url.rstrip("/") + "/"
        self.start_url = start_url.rstrip("/") + "/"

        self._traverser = traverser
        self._http_fetcher = http_fetcher
        self._html_parser = html_parser
        self._text_processor = text_processor
        self._output_writer = output_writer

        self._max_pages = max_pages
        self._max_depth = max_depth

        self._seen: set[str] = set()
        return None

    async def __aenter__(self) -> "Crawler":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self._http_fetcher.aclose()
        await self._output_writer.aclose()
        return None

    def crawl(self) -> None:
        pass
