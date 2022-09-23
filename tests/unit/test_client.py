from pathlib import Path
from typing import Any
import pytest
import httpx
from pytest_mock import MockerFixture
from conftest import MockResponse
from core.client import Client
from lxml import etree

from core.models.manga import Manga


class TestClient:
    @pytest.mark.asyncio
    async def test_get_manga_info(self, mocker: MockerFixture) -> None:
        mocker.patch.object(httpx.AsyncClient, "get", return_value=MockResponse(200))
        client: Client = Client()
        ret: Manga = await client.get_manga_info("Hello")
        assert ret.title == "Naruto"

    @pytest.mark.asyncio
    async def test_get_manga_info_http_error(self, mocker: MockerFixture) -> None:
        mocker.patch.object(httpx.AsyncClient, "get", return_value=MockResponse(404))
        client: Client = Client()
        ret: Manga = await client.get_manga_info("Hello")
        assert ret is None

    @pytest.mark.asyncio
    async def test_get_manga_info_bad_xml(self, mocker: MockerFixture) -> None:
        mocker.patch.object(httpx.AsyncClient, "get", return_value=MockResponse(415))
        client: Client = Client()
        ret: Manga = await client.get_manga_info("Hello")
        assert ret is None

    @pytest.mark.asyncio
    async def test_parse_xml(self) -> None:
        xml: etree._Element = etree.fromstring(
            Path("tests/samples/naruto.xml").read_text()
        )
        client: Client = Client()
        ret: Manga = await client._parse_xml(xml=xml)
        assert ret.title == "Naruto"
        assert ret.link == "https://mangasee123.com/manga/Naruto"
        assert ret.chapters[0].title == "Naruto Chapter 1"
        assert (
            ret.chapters[0].link
            == "https://mangasee123.com/read-online/Naruto-chapter-1.html"
        )
