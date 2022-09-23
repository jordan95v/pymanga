from dataclasses import dataclass
from datetime import datetime

__all__: list[str] = ["Chapter", "Manga"]


@dataclass
class Chapter:
    title: str | None = None
    link: str | None = None
    publication_date: datetime | None = None


@dataclass
class Manga:
    title: str | None = None
    link: str | None = None
    image: str | None = None
    chapters: list[Chapter] | None = None
