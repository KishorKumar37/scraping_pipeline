import asyncio
from typing import Optional


class RateLimiter:
    """
    Enforces a minimum interval between actions (here: HTTP requests).
    """

    def __init__(self, min_interval: float) -> None:
        self.min_interval = min_interval
        self._lock = asyncio.Lock()
        self._last_ts: Optional[float] = None

    async def wait(self) -> None:
        loop = asyncio.get_running_loop()
        async with self._lock:
            now = loop.time()
            if self._last_ts is None:
                self._last_ts = now
                return

            elapsed = now - self._last_ts
            if elapsed < self.min_interval:
                await asyncio.sleep(self.min_interval - elapsed)

            self._last_ts = loop.time()
