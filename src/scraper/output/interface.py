from abc import ABC, abstractmethod

from scraper.models import PageObject


class OutputWriter(ABC):
    @abstractmethod
    async def write(self, page_object: PageObject) -> None:
        """Persist a processed page object."""
        raise NotImplementedError

    async def aclose(self) -> None:
        """Close held resources."""
        return None

    async def __aenter__(self) -> "OutputWriter":
        """Enter the writer context."""
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        """Ensure resources are closed when leaving the context."""
        await self.aclose()
