from abc import ABC, abstractmethod


class TraversalStrategy(ABC):
    @abstractmethod
    def push(self, url: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def pop(self) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def is_empty(self) -> bool:
        raise NotImplementedError
