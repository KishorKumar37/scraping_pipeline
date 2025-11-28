import asyncio
import logging
import random
from typing import Optional

import httpx

from scraper.http.interface import HttpFetcher

logger = logging.getLogger(__name__)


class HttpxFetcher(HttpFetcher):
    def __init__(
        self,
        timeout: float = 3.0,
        min_request_interval: float | None = None,
        user_agent: str = "ai-collections-scraper/0.1",
        max_retries: int = 2,
        backoff_base: float = 0.5,
    ) -> None:
        """Initialize an AsyncClient with crawler-friendly defaults."""
        super().__init__(min_request_interval)
        self._max_retries = max(0, max_retries)
        self._backoff_base = max(0.0, backoff_base)
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers={
                "User-Agent": user_agent,
                "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
            },
            follow_redirects=True,
        )
        return None

    async def get(self, url: str) -> httpx.Response | None:
        """Fetch a URL with httpx and swallow expected errors."""
        attempt = 0
        while attempt <= self._max_retries:
            if self._rate_limiter is not None:
                await self._rate_limiter.wait()

            try:
                response: httpx.Response = await self._client.get(url)
                response.raise_for_status()
                return response
            except httpx.TimeoutException as e:
                logger.warning("Timeout while fetching %s: %s", url, e)
                retriable = True
            except httpx.HTTPStatusError as e:
                status: Optional[int] = e.response.status_code if e.response else None
                if status == 404:
                    logger.info("Not found (404) while fetching %s", url)
                    return None
                logger.warning("HTTP %s while fetching %s: %s", status, url, e)
                retriable = status is not None and status >= 500
            except httpx.RequestError as e:
                logger.warning("Request error while fetching %s: %s", url, e)
                retriable = True

            if not retriable or attempt == self._max_retries:
                logger.error("Giving up on %s after %s attempts", url, attempt + 1)
                return None

            delay = self._backoff_base * (2**attempt)
            delay += random.uniform(0, delay * 0.1) if delay > 0 else 0
            logger.debug("Retrying %s in %.2fs (attempt %s)", url, delay, attempt + 1)
            await asyncio.sleep(delay)
            attempt += 1

    async def aclose(self) -> None:
        """Close the underlying httpx client."""
        return await self._client.aclose()
