from aiofiles.threadpool.text import AsyncTextIOWrapper
from scraper.models import PageObject
from scraper.output.interface import OutputWriter
import aiofiles


class JsonlWriter(OutputWriter):
    def __init__(self, path: str) -> None:
        self.path: str = path
        self._file: AsyncTextIOWrapper | None = None
        return None

    async def write(self, page_object: PageObject) -> None:
        if not self._file:
            raise RuntimeError("JsonlWriter must be entered before writing")
        await self._file.write(page_object.model_dump_json() + "\n")
        return None

    async def __aenter__(self) -> "JsonlWriter":
        self._file = await aiofiles.open(file=self.path, mode="w")
        return self

    async def aclose(self) -> None:
        if self._file:
            return await self._file.close()
        return None
