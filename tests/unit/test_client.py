import pathlib
from typing import Any, Type
from unittest.mock import MagicMock
import pytest
from pytest_mock import MockerFixture
from requests_html import AsyncHTMLSession
from conftest import MockResponse
from pymanga import Client
from pymanga.models import Chapter
from pymanga.utils.exceptions import MangaNotFound


@pytest.mark.asyncio
class TestClient:
    async def test__call(self, mocker: MockerFixture) -> None:
        async def patch_html(*args: Any, **kwargs: Any) -> MockResponse:
            return MockResponse("fake_text", 200)

        client: Client = Client()
        mocker.patch.object(AsyncHTMLSession, "get", patch_html)
        await client._call("fake_url", AsyncHTMLSession())

    @pytest.mark.parametrize(
        "given, status_code, throwable, expected_length",
        [
            (pathlib.Path("tests/samples/bleach.xml"), 200, None, 3),
            (pathlib.Path("tests/samples/berserk.xml"), 200, None, 3),
            (pathlib.Path("tests/samples/bad.xml"), 200, None, 0),
            (None, 404, MangaNotFound, None),
        ],
    )
    async def test_get_chapters(
        self,
        client: Client,
        mocker: MockerFixture,
        given: pathlib.Path | None,
        status_code: int,
        throwable: Type[Exception] | None,
        expected_length: int | None,
    ) -> None:
        async def patch_html(*args: Any, **kwargs: Any) -> MockResponse:
            xml: str = given.read_text("utf-8") if given else ""
            return MockResponse(xml, status_code)

        mocker.patch.object(AsyncHTMLSession, "get", patch_html)
        if throwable:
            with pytest.raises(throwable):
                await client.get_chapters("bleach")
        else:
            chapters: list[Chapter] = await client.get_chapters("bleach")
            assert len(chapters) == expected_length

    async def test__aenter__(self) -> None:
        async with Client() as client:
            assert isinstance(client, Client)
            assert isinstance(client.session, AsyncHTMLSession)

    @pytest.mark.parametrize("throwable", [None, MangaNotFound])
    async def test__aexit__(
        self, mocker: MockerFixture, throwable: Type[Exception] | None
    ) -> None:
        close_spy: MagicMock = mocker.spy(AsyncHTMLSession, "close")
        if throwable:
            with pytest.raises(throwable):
                await Client().__aexit__(throwable, None, None)
        else:
            async with Client() as _:
                pass
            close_spy.assert_called_once()

    async def test_close(self, mocker: MockerFixture) -> None:
        close_spy: MagicMock = mocker.spy(AsyncHTMLSession, "close")
        client: Client = Client(session=AsyncHTMLSession())
        await client.close()
        close_spy.assert_called_once()

    async def test_download_chapter(
        self,
        client: Client,
        chapter: Chapter,
        mocker: MockerFixture,
        tmp_path: pathlib.Path,
    ) -> None:
        mocker.patch.object(
            Chapter, "get_images", return_value=["fake_url", "fake_url_2"]
        )
        mocker.patch.object(
            Client, "_call", return_value=MockResponse("fake_text", 200)
        )
        await client.download_chapter(chapter, tmp_path, 2)
        assert (tmp_path / "fake_chapter.cbz").exists()
