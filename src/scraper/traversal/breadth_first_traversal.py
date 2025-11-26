from scraper.traversal.interface import TraversalStrategy
from collections import deque


class BreadthFirstTraversalStrategy(TraversalStrategy):
    def __init__(self) -> None:
        self._queue: deque[str] = deque()
        return None

    def push(self, url: str) -> None:
        self._queue.append(url)
        return None

    def pop(self) -> str | None:
        if self.is_empty():
            return None
        return self._queue.popleft()

    def is_empty(self) -> bool:
        return len(self._queue) == 0
