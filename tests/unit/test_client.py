import pathlib
import httpx
import pytest
from pytest_mock import MockerFixture
from core import Client
from core.models import Chapter


@pytest.fixture
def client() -> Client:
    return Client()


class MockResponse:
    def __init__(self, text: str) -> None:
        self.text = text


@pytest.mark.asyncio
class TestClient:
    async def test_get_chapters(self, client: Client, mocker: MockerFixture) -> None:
        sample_xml: pathlib.Path = pathlib.Path("tests/samples/bleach.xml")
        mocker.patch.object(
            httpx.AsyncClient, "get", return_value=MockResponse(sample_xml.read_text())
        )
        chapters: list[Chapter] = [
            chapter async for chapter in client.get_chapters("bleach")
        ]
        assert len(chapters) == 698
        assert chapters[0].name == "Bleach Chapter 1"
