from pathlib import Path
from typing import Type
import httpx
import pytest
from pytest_mock import MockerFixture
from conftest import MockResponse
from pymanga.models import Chapter
from pymanga.utils.exceptions import ChapterError, ChapterNotFound


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
            mocker.patch.object(
                chapter, "_parse_html", return_value=(2, "", "fake_url")
            )
            mocker.patch.object(
                chapter,
                "_get_number_path",
                side_effect=["0001-001.png", "0001-002.png"],
            )
            imgs: list[str] = await chapter.get_images(session)
            assert imgs == [
                "https://fake_url/manga/fake/0001-001.png",
                "https://fake_url/manga/fake/0001-002.png",
            ]
        await session.aclose()

    @pytest.mark.parametrize(
        "given, expected",
        [
            ("Bleach-Bankai-Stories-Chapter-1", "Bleach-Bankai-Stories"),
            ("Bleach-Chapter-1", "Bleach"),
            ("Bleach-Chapter-1.5", "Bleach"),
        ],
    )
    async def test_slug(self, given: str, expected: str) -> None:
        chapter: Chapter = Chapter(given, "https://fake_url.com")
        assert chapter.slug == expected

    @pytest.mark.parametrize(
        "given, expected, throwable",
        [
            (Path("tests/samples/fake.html"), (2, "test", "fake_url"), None),
            (Path("tests/samples/fake_bad.html"), None, ChapterError),
            (Path("tests/samples/fake_nothing.html"), None, ChapterError),
        ],
    )
    async def test__parse_html(
        self,
        chapter: Chapter,
        given: Path,
        expected: tuple[int, str, str] | None,
        throwable: Type[Exception] | None,
    ) -> None:
        res: httpx.Response = MockResponse(given.read_text("utf-8"), 200)
        if throwable:
            with pytest.raises(throwable):
                await chapter._parse_html(res)
        else:
            assert await chapter._parse_html(res) == expected

    @pytest.mark.parametrize(
        "given, image_number, expected",
        [
            (Chapter(name="Bleach-4", url="fake_url"), 77, "0004-077.png"),
            (Chapter(name="Bleach-4.5", url="fake_url"), 189, "0004.5-189.png"),
        ],
    )
    async def test__get_number_path(
        self, given: Chapter, image_number: int, expected: str
    ) -> None:
        assert given._get_number_path(image_number) == expected
