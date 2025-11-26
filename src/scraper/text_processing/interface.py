from abc import ABC, abstractmethod

from scraper.models import Page, Signals


class TextProcessor(ABC):
    def get_signals(self, page: Page) -> tuple[Page, Signals]:
        page.text = self._process_text(page.text)
        signals: Signals = self._generate_signals(page)
        return (page, signals)

    @abstractmethod
    def _process_text(self, text: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def _generate_signals(self, page: Page) -> Signals:
        raise NotImplementedError
