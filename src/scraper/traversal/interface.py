from abc import ABC, abstractmethod


class TraversalStrategy(ABC):
    @abstractmethod
    def push(self, url: str) -> None:
        """Add a URL to the traversal frontier."""
        raise NotImplementedError

    @abstractmethod
    def pop(self) -> str | None:
        """Remove and return the next URL to visit."""
        raise NotImplementedError

    @abstractmethod
    def is_empty(self) -> bool:
        """Return True when the frontier has no work left."""
        raise NotImplementedError
