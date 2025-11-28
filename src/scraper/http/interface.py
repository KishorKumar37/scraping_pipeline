from abc import ABC, abstractmethod
from httpx import Response
from scraper.http.rate_limiter import RateLimiter


class HttpFetcher(ABC):
    def __init__(self, min_request_interval: float | None = None) -> None:
        if min_request_interval:
            self._rate_limiter = RateLimiter(min_interval=min_request_interval)
        else:
            self._rate_limiter = None
        return None

    @abstractmethod
    async def get(self, url: str) -> Response | None:
        """Fetch a URL and return the response or None on failure."""
        raise NotImplementedError

    async def aclose(self) -> None:
        """Close held network resources."""
        return None

    async def __aenter__(self) -> "HttpFetcher":
        """Enter the fetcher context."""
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        """Exit the fetcher context and close resources."""
        await self.aclose()
