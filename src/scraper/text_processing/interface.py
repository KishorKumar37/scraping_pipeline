from abc import ABC, abstractmethod

from scraper.models import Page, Signals


class TextProcessor(ABC):
    def get_signals(self, page: Page) -> tuple[Page, Signals]:
        """Run processing pipeline and derive structured signals."""
        page.text = self._process_text(page.text)
        signals: Signals = self._generate_signals(page)
        return (page, signals)

    @abstractmethod
    def _process_text(self, text: str) -> str:
        """Clean or transform the page text."""
        raise NotImplementedError

    @abstractmethod
    def _generate_signals(self, page: Page) -> Signals:
        """Extract analytics or metadata from processed page."""
        raise NotImplementedError
