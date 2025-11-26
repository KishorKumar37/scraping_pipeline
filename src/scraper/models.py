from pydantic import BaseModel


class Page(BaseModel):
    title: str
    url: str
    text: str


class Signals(BaseModel):
    word_count: int
    character_count: int


class PageObject(Page, Signals):
    pass
