import argparse
import asyncio

from scraper.crawler_builder import CrawlerBuilder
from scraper.http.httpx_fetcher import HttpxFetcher
from scraper.output.jsonl_writer import JsonlWriter
from scraper.parsers.basic_html_parser import BasicHtmlParser
from scraper.text_processing.basic_text_processor import BasicTextProcessor


def parse_args() -> argparse.Namespace:
    """Parse command-line options for the crawler CLI."""
    parser = argparse.ArgumentParser(description="Run the scraping crawler.")
    parser.add_argument(
        "--input-url",
        required=True,
        help="Seed URL to begin crawling (also determines the allowed domain).",
    )
    parser.add_argument(
        "--outputpath",
        required=True,
        help="Destination path for the JSONL output file.",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help="Optional maximum crawl depth; omit to crawl without a depth limit.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Optional maximum number of pages to persist; omit for no limit.",
    )
    return parser.parse_args()


async def run_crawler(args: argparse.Namespace) -> None:
    """Instantiate dependencies and execute the crawler."""
    builder = CrawlerBuilder(
        domain_url=args.input_url,
        start_url=args.input_url,
        output_path=args.outputpath,
    )
    if args.max_depth is not None:
        builder = builder.with_max_depth(args.max_depth)
    if args.max_pages is not None:
        builder = builder.with_max_pages(args.max_pages)

    crawler = (
        builder.with_fetcher(HttpxFetcher(timeout=10.0))
        .with_html_parser(BasicHtmlParser())
        .with_text_processor(BasicTextProcessor())
        .with_output_writer(JsonlWriter(args.outputpath))
        .build()
    )

    async with crawler:
        await crawler.crawl()


def main() -> None:
    """Entry point for the CLI."""
    args = parse_args()
    asyncio.run(run_crawler(args))


if __name__ == "__main__":
    main()
