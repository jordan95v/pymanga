from typing import Any
import pytest
from dataclasses import dataclass
from pymanga import Client
from requests import HTTPError

from pymanga.models.manga import Chapter


@pytest.fixture
def client() -> Client:
    return Client()


@pytest.fixture
def chapter() -> Chapter:
    return Chapter(name="fake_chapter", url="https://fake_url.com")


@dataclass
class MockResponse:
    text: str
    status_code: int

    def raise_for_status(self) -> None:
        if self.status_code != 200:
            raise HTTPError("fake_error")

    @property
    def content(self) -> bytes:
        return bytes(self.text, "utf-8")


class MockElement:
    @property
    def attrs(self) -> dict[str, Any]:
        return {"src": "https://fake_url.com"}


class HTMLMock:
    async def arender(self, *args: Any, **kwargs: Any) -> None:
        pass

    def find(self, *args: Any, **kwargs: Any) -> list[MockElement]:
        return [MockElement() for _ in range(2)]


@dataclass
class MockHTMLResponse:
    status_code: int

    @property
    def html(self) -> HTMLMock:
        return HTMLMock()

    def raise_for_status(self) -> None:
        if self.status_code != 200:
            raise HTTPError("fake_error")
