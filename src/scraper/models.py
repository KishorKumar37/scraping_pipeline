from pydantic import BaseModel


class Page(BaseModel):
    title: str
    url: str
    timestamp: str
    text: str


class Signals(BaseModel):
    word_count: int
    character_count: int
    estimated_reading_time: float
    language: str
    content_type: str


class PageObject(Page, Signals):
    pass
