import httpx
import logging

from scraper.http.interface import HttpFetcher

logger = logging.getLogger(__name__)


class HttpxFetcher(HttpFetcher):
    def __init__(
        self,
        timeout: float = 3.0,
        user_agent: str = "ai-collections-scraper/0.1",
    ) -> None:
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
        try:
            response: httpx.Response = await self._client.get(url)
            response.raise_for_status()
        except httpx.TimeoutException as e:
            logging.warning(f"Timeout while fetching {url}: {e}")
            return None
        except httpx.HTTPStatusError as e:
            status = e.response.status_code if e.response else "unknown"
            if status == 404:
                logging.info(f"Not found (404) while fetching {url}")
            else:
                logging.warning(f"HTTP {status} while fetching {url}: {e}")
            return None
        except httpx.RequestError as e:
            logging.warning(f"Request error while fetching {url}: {e}")
            return None

        return response

    async def aclose(self) -> None:
        return await self._client.aclose()
