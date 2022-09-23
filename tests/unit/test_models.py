from datetime import datetime
from typing import Any
import pytest
from core.models.manga import Manga, Chapter


class TestModels:
    def test_manga_model(self) -> None:
        manga: Manga = Manga(title="Naruto", link="Naruto/Scan", image="Naruto.jpg")
        assert manga.title == "Naruto"
        assert manga.link == "Naruto/Scan"
        assert manga.image == "Naruto.jpg"
        assert manga.chapters is None

    def test_chapter_model(self) -> None:
        chapter: Chapter = Chapter(
            title="Jujutsu 01",
            link="Jujutsu 01/Scan",
            publication_date=datetime(2022, 9, 23),
        )
        assert chapter.title == "Jujutsu 01"
        assert chapter.link == "Jujutsu 01/Scan"
        assert chapter.publication_date == datetime(2022, 9, 23)
