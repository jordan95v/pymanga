from pathlib import Path
from unittest.mock import MagicMock
import pytest
import httpx
from pytest_mock import MockerFixture
from conftest import MockResponse
from core.client import Client
from lxml import etree
from core.models.manga import Manga
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
    async def test_parse_xml(self, client: Client) -> None:
        xml: etree._Element = etree.fromstring(
            Path("tests/samples/naruto.xml").read_text()
        )
        ret: Manga = await client._parse_xml(xml=xml)
        assert ret.title == "Naruto"
        assert ret.link == "https://mangasee123.com/manga/Naruto"
        assert ret.chapters[0].title == "Naruto Chapter 1"
        assert (
            ret.chapters[0].link
            == "https://mangasee123.com/read-online/Naruto-chapter-1.html"
        )

    @pytest.mark.asyncio
    async def test_parse_xml_none(self, client: Client) -> None:
        xml: etree._Element = etree.fromstring("<xml><a>Hello</a></xml>")
        with pytest.raises(ParsingError):
            await client._parse_xml(xml=xml)
