import pathlib
from dataclasses import dataclass
from typing import Type
import httpx
import pytest
from pytest_mock import MockerFixture
from core import Client
from core.models import Chapter
from core.utils.exceptions import MangaNotFound


@pytest.fixture
def client() -> Client:
    return Client()


@dataclass
class MockResponse:
    text: str
    status_code: int

    def raise_for_status(self) -> None:
        if self.status_code != 200:
            raise httpx.HTTPError("fake_error")


@pytest.mark.asyncio
class TestClient:
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
