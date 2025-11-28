from scraper.traversal.interface import TraversalStrategy
from collections import deque


class BreadthFirstTraversalStrategy(TraversalStrategy):
    def __init__(self) -> None:
        """Initialize an empty deque-backed queue."""
        self._queue: deque[str] = deque()
        return None

    def push(self, url: str) -> None:
        """Enqueue a URL at the tail."""
        self._queue.append(url)
        return None

    def pop(self) -> str | None:
        """Dequeue the next URL in breadth-first order."""
        if self.is_empty():
            return None
        return self._queue.popleft()

    def is_empty(self) -> bool:
        """Return True when the queue has no pending URLs."""
        return len(self._queue) == 0
