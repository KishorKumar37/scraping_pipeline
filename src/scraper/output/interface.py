from abc import ABC, abstractmethod

from scraper.models import PageObject


class OutputWriter(ABC):
    @abstractmethod
    async def write(self, page_object: PageObject) -> None:
        raise NotImplementedError

    async def aclose(self) -> None:
        return None

    async def __aenter__(self) -> "OutputWriter":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()
