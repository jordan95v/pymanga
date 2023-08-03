import pathlib
from typing import Type
from unittest.mock import MagicMock
import httpx
import pytest
from pytest_mock import MockerFixture
from conftest import MockResponse
from pymanga import Client
from pymanga.models import Chapter
from pymanga.utils.exceptions import MangaNotFound


@pytest.mark.asyncio
class TestClient:
    async def test__call(self, mocker: MockerFixture) -> None:
        client: Client = Client()
        mocker.patch.object(
            httpx.AsyncClient, "get", return_value=MockResponse("fake_text", 200)
        )
        await client._call("fake_url", httpx.AsyncClient())

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
        xml: str = given.read_text("utf-8") if given else ""
        mocker.patch.object(
            httpx.AsyncClient, "get", return_value=MockResponse(xml, status_code)
        )
        if throwable:
            with pytest.raises(throwable):
                await client.get_chapters("bleach")
        else:
            chapters: list[Chapter] = await client.get_chapters("bleach")
            assert len(chapters) == expected_length

    async def test__aenter__(self) -> None:
        async with Client() as client:
            assert isinstance(client, Client)
            assert isinstance(client.session, httpx.AsyncClient)

    @pytest.mark.parametrize("throwable", [None, MangaNotFound])
    async def test__aexit__(
        self, mocker: MockerFixture, throwable: Type[Exception] | None
    ) -> None:
        close_spy: MagicMock = mocker.spy(httpx.AsyncClient, "aclose")
        if throwable:
            with pytest.raises(throwable):
                await Client().__aexit__(throwable, None, None)
        else:
            async with Client():
                pass
            close_spy.assert_called_once()

    async def test_close(self, mocker: MockerFixture) -> None:
        close_spy: MagicMock = mocker.spy(httpx.AsyncClient, "aclose")
        client: Client = Client(session=httpx.AsyncClient())
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
        assert (tmp_path / "fake-chapter-1.cbz").exists()
