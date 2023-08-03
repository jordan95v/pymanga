from dataclasses import dataclass
import httpx
import pytest
from pymanga import Client
from pymanga.models.manga import Chapter


@pytest.fixture
def client() -> Client:
    return Client()


@pytest.fixture
def chapter() -> Chapter:
    return Chapter(name="fake chapter 1", url="https://fake_url.com")


@dataclass
class MockResponse:
    text: str
    status_code: int

    def raise_for_status(self) -> None:
        if self.status_code != 200:
            raise httpx.HTTPError("fake_error")

    @property
    def content(self) -> bytes:
        return bytes(self.text, "utf-8")
