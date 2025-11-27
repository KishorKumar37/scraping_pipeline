from abc import ABC, abstractmethod
from httpx import Response


class HttpFetcher(ABC):
    @abstractmethod
    async def get(self, url: str) -> Response | None:
        raise NotImplementedError

    async def aclose(self) -> None:
        return None

    async def __aenter__(self) -> "HttpFetcher":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()
