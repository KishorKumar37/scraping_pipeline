## Scraping Pipeline

### 1. Site Choice
I targeted **quotes.toscrape.com**, a sandbox site explicitly built for scraping demos. It exposes consistent HTML structure and meaningful text, which makes it ideal for showing how to transform raw pages into AI-friendly documents without legal risk.

### 2. How to Run

#### Dependencies
- Python 3.11+
- [`uv`](https://github.com/astral-sh/uv) (or plain `pip`) for dependency management

Install the project in editable mode:

```bash
uv pip install -e .
```

Run the crawler from the repo root:

```bash
uv run python main.py \
  --input-url https://quotes.toscrape.com \
  --outputpath pages.jsonl \
  --max-pages 100 \
  --max-depth 3 \
  --log-level INFO
```

Arguments:
- `--input-url`: Seed URL; also defines allowed domain.
- `--outputpath`: Destination JSONL file.
- `--max-pages`, `--max-depth`: Optional caps (omit for full crawl).
- `--log-level`: `DEBUG/INFO/WARN/ERROR`.

### 3. Data Schema
Each JSONL record follows this schema:

| Field | Description |
| --- | --- |
| `title` | Page title text |
| `url` | Canonical URL of the crawled page |
| `timestamp` | ISO-8601 timestamp when fetched |
| `text` | Main body text with boilerplate removed |
| `word_count` | Number of whitespace-separated words |
| `character_count` | Character length of `text` |
| `estimated_reading_time` | Minutes to read (200 WPM heuristic) |
| `language` | Language code detected via `langdetect` |
| `content_type` | Heuristic classification (article, doc_page, etc.) |

### 4. Design Decisions
- **Page selection**: URLs are normalized, constrained to the seed domain, and we skip obvious non-content paths (login/tag). A BFS traversal with a visited set prevents duplicates and respects optional depth/page caps.
- **Main content extraction**: `BasicHtmlParser` strips known header/footer selectors on the first page, then extracts `<body>` text. The text processor removes extra whitespace before generating signals.
- **AI workflow alignment**:
  - Metadata (`title`, `url`, `timestamp`) provides traceability.
  - Signals (`word_count`, `language`, `content_type`, reading time) enable filtering/ranking for RAG, search, or fine-tuning jobs.
  - JSONL output is easy to load into downstream tooling.
- **Robustness**: `HttpxFetcher` enforces throttling plus retries with exponential backoff; the crawler logs progress at INFO/DEBUG levels and treats fetch/parse errors as non-fatal.

### 5. Low-Level Design
- **Crawler**: `CrawlerBuilder` wires the fetcher, parser, text processor, traversal strategy, and writer. `Crawler` orchestrates the crawl loop, keeps a depth map and seen set, and coordinates context management for each I/O-heavy dependency.
- **Fetching**: `HttpxFetcher` wraps `httpx.AsyncClient`, adds rate limiting, retries with exponential backoff, and emits structured logs for each outcome. The fetcher exposes `async with` hooks so the crawler can manage its lifecycle.
- **Parsing & Processing**: `BasicHtmlParser` uses BeautifulSoup for extraction and a small ruleset that learns which selectors to strip on the first page. `BasicTextProcessor` applies regex-based whitespace cleanup and a signal pipeline (counts, language via `langdetect`, reading time, content type heuristics).
- **Traversal**: Strategy interface + BFS deque implementation keep frontier logic swappable. Links are normalized via `scraper.utils.urls` helpers before being enqueued.
- **Output**: `JsonlWriter` wraps `aiofiles` for asynchronous writes; it enforces `async with` usage to ensure file handles close cleanly.

### 6. Future Work
- Add parser plugins for richer metadata (authors, tags).
- Persist crawl frontier state for resumable runs and scheduling.
- Integrate monitoring + alerting for failures or slowdowns.
- Deduplicate across multiple domains and feed into a central store.
- Add automated tests and contract-based schema validation.
