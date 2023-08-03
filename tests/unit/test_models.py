from pathlib import Path
from typing import Type
import httpx
import pytest
from pytest_mock import MockerFixture
from conftest import MockResponse
from pymanga.models import Chapter
from pymanga.utils.exceptions import ChapterNotFound


@pytest.mark.asyncio
class TestChapter:
    @pytest.mark.parametrize(
        "status_code, throwable",
        [
            (200, False),
            (404, ChapterNotFound),
        ],
    )
    async def test_get_images(
        self,
        chapter: Chapter,
        mocker: MockerFixture,
        status_code: int,
        throwable: Type[Exception],
    ) -> None:
        mocker.patch.object(
            httpx.AsyncClient,
            "get",
            return_value=MockResponse(
                Path("tests/samples/fake.html").read_text(), status_code
            ),
        )
        session: httpx.AsyncClient = httpx.AsyncClient()

        if throwable:
            with pytest.raises(throwable):
                await chapter.get_images(session)
        else:
            imgs: list[str] = await chapter.get_images(session)
            assert imgs == [
                "https://fake_url/manga/Fake/0001-001.png",
                "https://fake_url/manga/Fake/0001-002.png",
            ]
        await session.aclose()

    @pytest.mark.parametrize(
        "given, expected",
        [
            ("Bleach Bankai Stories Chapter 1", "Bleach-Bankai-Stories"),
            ("Bleach Chapter 1", "Bleach"),
            ("Bleach Chapter 1.5", "Bleach"),
        ],
    )
    async def test_slug(self, given: str, expected: str) -> None:
        chapter: Chapter = Chapter(given, "https://fake_url.com")
        assert chapter.slug == expected

    @pytest.mark.parametrize(
        "given, expected",
        [
            ("Bleach Bankai Stories Chapter 1", 1),
            ("Bleach Chapter 1", 1),
            ("Bleach Chapter 1.5", 1.5),
        ],
    )
    async def test_number(self, given: str, expected: int | float) -> None:
        chapter: Chapter = Chapter(given, "https://fake_url.com")
        assert chapter.number == expected
