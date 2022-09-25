import asyncio
from datetime import datetime
from multiprocessing import managers
from typing import Any
from unittest.mock import MagicMock
import pytest
from pytest_mock import MockerFixture
from conftest import MockResponse
from requests_html import AsyncHTMLSession
from core.models.manga import Manga, Chapter
from core.utils.exceptions import ChapterNotFound


class TestManga:
    def test_manga_model(self) -> None:
        manga: Manga = Manga(
            title="Naruto",
            link="Naruto/Scan",
            image="Naruto.jpg",
            start_date="2022-09-25",
        )
        assert manga.title == "Naruto"
        assert manga.link == "Naruto/Scan"
        assert manga.image == "Naruto.jpg"
        assert manga.chapters is None
        assert manga.description is None
        assert manga.start_date == datetime(2022, 9, 25).date()
        assert manga.end_date is None


class TestChapter:
    def test_chapter_model(self) -> None:
        chapter: Chapter = Chapter(
            title="Jujutsu 01",
            link="Jujutsu 01/Scan",
            publication_date=datetime(2022, 9, 23),
        )
        assert chapter.title == "Jujutsu 01"
        assert chapter.link == "Jujutsu 01/Scan"
        assert chapter.publication_date == datetime(2022, 9, 23)

    @pytest.mark.parametrize(
        "status_code, throwable", [(200, None), (401, ChapterNotFound)]
    )
    @pytest.mark.asyncio
    async def test_get_chapter_image(
        self,
        status_code: int,
        throwable: Exception | None,
        mocker: MockerFixture,
    ) -> None:
        chapter: Chapter = Chapter()

        async def patch_html(*args: Any, **kwargs: Any) -> None:
            return MockResponse(status_code)

        mocker.patch.object(AsyncHTMLSession, "get", patch_html)
        close_js_spy: MagicMock = mocker.spy(AsyncHTMLSession, "close")
        if throwable:
            with pytest.raises(throwable):
                await chapter.images_links()
        else:
            ret: list[str] = await chapter.images_links()
            assert ret == ["naruto", "sasuke"]
            assert close_js_spy.call_count == 1
