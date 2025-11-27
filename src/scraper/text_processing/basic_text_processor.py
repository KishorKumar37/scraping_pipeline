import re
from scraper.models import Page, Signals
from scraper.text_processing.interface import TextProcessor


class BasicTextProcessor(TextProcessor):

    def _process_text(self, text: str) -> str:
        return self._remove_spaces(text)

    def _generate_signals(self, page: Page) -> Signals:
        character_count: int = len(page.text)
        word_count: int = len(page.text.split())
        signals: Signals = Signals(
            word_count=word_count, character_count=character_count
        )

        return signals

    def _remove_spaces(self, text: str) -> str:
        text = text.strip()
        text = re.sub(pattern=r"(\s)\1+", repl=r"\1", string=text)
        return text
