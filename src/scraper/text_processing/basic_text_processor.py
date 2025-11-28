import re
from scraper.models import Page, Signals
from scraper.text_processing.interface import TextProcessor

from langdetect import detect, LangDetectException


class BasicTextProcessor(TextProcessor):

    def _process_text(self, text: str) -> str:
        """Normalize whitespace before downstream processing."""
        return self._remove_spaces(text)

    def _generate_signals(self, page: Page) -> Signals:
        """Produce baseline analytics such as counts, language, and type."""
        character_count: int = len(page.text)
        word_count: int = len(page.text.split())
        language = self._detect_language(page.text)
        signals: Signals = Signals(
            word_count=word_count,
            character_count=character_count,
            language=language,
            estimated_reading_time=self._estimate_reading_time_minutes(word_count),
            content_type=self._infer_content_type(page.url, word_count),
        )

        return signals

    def _remove_spaces(self, text: str) -> str:
        """Collapse repeated whitespace and trim the text."""
        text = text.strip()
        text = re.sub(pattern=r"(\s)\1+", repl=r"\1", string=text)
        return text

    def _detect_language(self, text: str) -> str:
        """Detect the language of the text, falling back to 'unknown'."""
        try:
            return detect(text)
        except LangDetectException:
            return "unknown"

    def _estimate_reading_time_minutes(self, word_count: int) -> float:
        """Estimate reading time assuming roughly 200 WPM."""
        if word_count <= 0:
            return 0.0
        return round(word_count / 200.0, 2)

    def _infer_content_type(self, url: str, word_count: int) -> str:
        """Guess content type using URL cues and word count."""
        path = url.lower()

        if "/docs/" in path or "/documentation/" in path:
            return "doc_page"
        if "/blog/" in path or "/posts/" in path or "/article/" in path:
            return "article"
        if "/product" in path or "/pricing" in path:
            return "product_page"
        if "/help" in path or "/faq" in path or "/support" in path:
            return "help_page"

        if word_count > 800:
            return "long_form"
        elif word_count > 200:
            return "content_page"
        else:
            return "other"
