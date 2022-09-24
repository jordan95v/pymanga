from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock
import pytest
import httpx
from pytest_mock import MockerFixture
from conftest import MockResponse
from requests_html import AsyncHTMLSession
from core.models.manga import Manga, Chapter
from core.utils.exceptions import ChapterNotFound


@pytest.fixture
def chapter() -> Chapter:
    return Chapter(
        title="Jujutsu 01",
        link="Jujutsu 01/Scan",
        publication_date=datetime(2022, 9, 23),
    )


class TestManga:
    def test_manga_model(self) -> None:
        manga: Manga = Manga(title="Naruto", link="Naruto/Scan", image="Naruto.jpg")
        assert manga.title == "Naruto"
        assert manga.link == "Naruto/Scan"
        assert manga.image == "Naruto.jpg"
        assert manga.chapters is None


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
        chapter: Chapter,
        status_code: int,
        throwable: Exception | None,
        mocker: MockerFixture,
    ) -> None:
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

    @pytest.mark.asyncio
    async def test_download_image(
        self, chapter: Chapter, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        async def patch_images() -> list[str]:
            return ["hello.jpg", "joaquim.jpg"]

        mocker.patch.object(httpx.AsyncClient, "get", return_value=MockResponse(200))
        mocker.patch.object(chapter, "images_links", side_effect=patch_images)

        await chapter.download_images(tmp_path)
        output: Path = tmp_path / f"{chapter.title}.zip"
        assert output.exists()
