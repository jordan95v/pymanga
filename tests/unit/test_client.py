import asyncio
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock
import httpx
import pytest
from pytest_mock import MockerFixture
from lxml import etree
from conftest import MockResponse
from core.client import Client
from core.models.manga import Chapter, Manga
from core.utils.exceptions import MangaNotFound, ParsingError


@pytest.fixture
def client() -> Client:
    return Client()


class TestClient:
    @pytest.mark.asyncio
    async def test__aenter__(self, client: Client) -> None:
        assert isinstance(await client.__aenter__(), Client)

    @pytest.mark.asyncio
    async def test__aexit__(self, mocker: MockerFixture) -> None:
        close_spy: MagicMock = mocker.spy(httpx.AsyncClient, "aclose")
        async with Client() as _:
            ...
        assert close_spy.call_count == 1

    @pytest.mark.asyncio
    async def test__aexit__error(self, client: Client, mocker: MockerFixture) -> None:
        with pytest.raises(TypeError):
            await client.__aexit__(TypeError, "yo", None)

    @pytest.mark.asyncio
    async def test_aclose(self, client: Client, mocker: MockerFixture) -> None:
        close_spy: MagicMock = mocker.spy(httpx.AsyncClient, "aclose")
        await client.close()
        assert close_spy.call_count == 1

    @pytest.mark.parametrize(
        "status_code, throwable",
        [
            (200, None),
            (404, MangaNotFound),
        ],
    )
    @pytest.mark.asyncio
    async def test_get_manga_info(
        self,
        client: Client,
        status_code: int,
        throwable: Exception | None,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch.object(
            httpx.AsyncClient, "get", return_value=MockResponse(status_code)
        )
        if throwable:
            with pytest.raises(throwable):
                await client.get_manga_info("Naruto")
        else:
            ret: Manga = await client.get_manga_info("Naruto")
            assert ret.title == "Naruto"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "status_code, throwable",
        [
            (200, None),
            (404, MangaNotFound),
        ],
    )
    async def test_get_info(
        self,
        client: Client,
        status_code: int,
        throwable: Exception | None,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch.object(
            httpx.AsyncClient, "get", return_value=MockResponse(status_code)
        )
        if throwable:
            with pytest.raises(MangaNotFound):
                await client._get_info("Naruto")
        else:
            res: dict[str, Any] = await client._get_info("Naruto")
            assert res["start_date"] == "1999-09-21"

    @pytest.mark.asyncio
    async def test_parse_xml(self, client: Client) -> None:
        xml: etree._Element = etree.fromstring(
            Path("tests/samples/naruto.xml").read_text()
        )
        ret: Manga = await client._parse_xml(xml=xml)
        assert ret["title"] == "Naruto"
        assert ret["link"] == "https://mangasee123.com/manga/Naruto"
        assert ret["chapters"][0].title == "Naruto Chapter 1"

    @pytest.mark.asyncio
    async def test_parse_xml_none(self, client: Client) -> None:
        xml: etree._Element = etree.fromstring("<xml><a>Hello</a></xml>")
        with pytest.raises(ParsingError):
            await client._parse_xml(xml=xml)

    @pytest.mark.asyncio
    async def test_download_image(
        self, client: Client, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        chapter: Chapter = Chapter()

        async def patch_images() -> list[str]:
            return ["hello.jpg", "joaquim.jpg"]

        mocker.patch.object(httpx.AsyncClient, "get", return_value=MockResponse(200))
        mocker.patch.object(Chapter, "images_links", side_effect=patch_images)

        await client.download_images(tmp_path, chapter)
        output: Path = tmp_path / f"{chapter.title}.cbz"
        assert output.exists()

    @pytest.mark.asyncio
    async def test_call(self, client: Client, mocker: MockerFixture) -> None:
        sem: asyncio.Semaphore = asyncio.Semaphore(10)
        mocker.patch.object(httpx.AsyncClient, "get", return_value=MockResponse(200))
        acquire_spy: MagicMock = mocker.spy(sem, "acquire")
        release_spy: MagicMock = mocker.spy(sem, "release")
        ret: httpx.Response = await client._call("hello", sem)
        assert acquire_spy.call_count == 1
        assert release_spy.call_count == 1
        assert ret.content == b"hello joaquim"
