from scraper.http.interface import HttpFetcher
from scraper.output.interface import OutputWriter
from scraper.parsers.interface import HtmlParser
from scraper.text_processing.interface import TextProcessor
from scraper.traversal.breadth_first_traversal import BreadthFirstTraversalStrategy
from scraper.traversal.interface import TraversalStrategy

from .crawler import Crawler


class CrawlerBuilder:
    """
    Builder for Crawler.
    Lets you configure components & parameters with a fluent API,
    and then build a fully-wired Crawler instance.
    """

    def __init__(self, domain_url: str, start_url: str) -> None:
        self._domain_url = domain_url
        self._start_url = start_url

        # defaults
        self._max_pages: int = 100
        self._max_depth: int = 3
        self._concurrency: int = 5

        self._traverser: TraversalStrategy | None = None
        self._http_fetcher: HttpFetcher | None = None
        self._html_parser: HtmlParser | None = None
        self._text_processor: TextProcessor | None = None
        self._output_writer: OutputWriter | None = None

    def with_max_pages(self, max_pages: int) -> "CrawlerBuilder":
        self._max_pages = max_pages
        return self

    def with_max_depth(self, max_depth: int) -> "CrawlerBuilder":
        self._max_depth = max_depth
        return self

    def with_concurrency(self, concurrency: int) -> "CrawlerBuilder":
        self._concurrency = concurrency
        return self

    def with_traversal(self, traverser: TraversalStrategy) -> "CrawlerBuilder":
        self._traverser = traverser
        return self

    def with_fetcher(self, fetcher: HttpFetcher) -> "CrawlerBuilder":
        self._http_fetcher = fetcher
        return self

    def with_html_parser(self, parser: HtmlParser) -> "CrawlerBuilder":
        self._html_parser = parser
        return self

    def with_text_processor(self, processor: TextProcessor) -> "CrawlerBuilder":
        self._text_processor = processor
        return self

    def with_output_writer(self, writer: OutputWriter) -> "CrawlerBuilder":
        self._output_writer = writer
        return self

    def build(self) -> Crawler:
        """
        Build and return a Crawler instance, filling in any missing components
        with sensible defaults.
        """

        # TODO : Substitute defaults for remaining components
        traverser = self._traverser or BreadthFirstTraversalStrategy()
        http_fetcher = self._http_fetcher
        html_parser = self._html_parser
        text_processor = self._text_processor
        output_writer = self._output_writer

        return Crawler(
            domain_url=self._domain_url,
            start_url=self._start_url,
            traverser=traverser,
            http_fetcher=http_fetcher,
            html_parser=html_parser,
            text_processor=text_processor,
            output_writer=output_writer,
            max_pages=self._max_pages,
            max_depth=self._max_depth,
        )
