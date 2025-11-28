from scraper.http.httpx_fetcher import HttpxFetcher
from scraper.http.interface import HttpFetcher
from scraper.output.interface import OutputWriter
from scraper.output.jsonl_writer import JsonlWriter
from scraper.parsers.basic_html_parser import BasicHtmlParser
from scraper.parsers.interface import HtmlParser
from scraper.text_processing.basic_text_processor import BasicTextProcessor
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

    def __init__(self, domain_url: str, start_url: str, output_path: str) -> None:
        """Initialize builder defaults and user-provided URLs."""
        self._domain_url: str = domain_url
        self._start_url: str = start_url
        self._output_path: str = output_path

        self._max_pages: int | None = None
        self._max_depth: int | None = None
        self._concurrency: int = 5

        self._traverser: TraversalStrategy | None = None
        self._http_fetcher: HttpFetcher | None = None
        self._html_parser: HtmlParser | None = None
        self._text_processor: TextProcessor | None = None
        self._output_writer: OutputWriter | None = None

    def with_max_pages(self, max_pages: int | None) -> "CrawlerBuilder":
        """Set an optional cap on how many pages to persist."""
        self._max_pages = max_pages
        return self

    def with_max_depth(self, max_depth: int | None) -> "CrawlerBuilder":
        """Set an optional traversal depth limit."""
        self._max_depth = max_depth
        return self

    def with_concurrency(self, concurrency: int) -> "CrawlerBuilder":
        """Set desired concurrency (currently unused)."""
        self._concurrency = concurrency
        return self

    def with_traversal(self, traverser: TraversalStrategy) -> "CrawlerBuilder":
        """Inject a traversal strategy implementation."""
        self._traverser = traverser
        return self

    def with_fetcher(self, fetcher: HttpFetcher) -> "CrawlerBuilder":
        """Inject an HTTP fetcher implementation."""
        self._http_fetcher = fetcher
        return self

    def with_html_parser(self, parser: HtmlParser) -> "CrawlerBuilder":
        """Inject an HTML parser implementation."""
        self._html_parser = parser
        return self

    def with_text_processor(self, processor: TextProcessor) -> "CrawlerBuilder":
        """Inject a text processor implementation."""
        self._text_processor = processor
        return self

    def with_output_writer(self, writer: OutputWriter) -> "CrawlerBuilder":
        """Inject an output writer implementation."""
        self._output_writer = writer
        return self

    def build(self) -> Crawler:
        """Create a crawler, filling any missing components with defaults."""

        traverser = self._traverser or BreadthFirstTraversalStrategy()
        http_fetcher = self._http_fetcher or HttpxFetcher()
        html_parser = self._html_parser or BasicHtmlParser()
        text_processor = self._text_processor or BasicTextProcessor()
        output_writer = self._output_writer or JsonlWriter(path=self._output_path)

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
