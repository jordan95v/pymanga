import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import httpx
import requests

__all__: list[str] = ["MockResponse", "MockElement", "MockHTML"]


@dataclass
class MockElement:
    src: str

    @property
    def attrs(self) -> dict[str, str]:
        return dict(src=self.src)


@dataclass
class MockHTML:
    async def arender(self, *args: Any, **kwargs: Any) -> None:
        pass

    def find(self, *args: Any, **kwargs: Any) -> list[MockElement]:
        return [MockElement("naruto"), MockElement("sasuke")]


@dataclass
class MockResponse:
    status_code: int

    def raise_for_status(self) -> None:
        if self.status_code == 404:
            raise httpx.HTTPError("yo")
        elif self.status_code == 401:
            raise requests.HTTPError()

    @property
    def text(self) -> str:
        return Path("tests/samples/naruto.xml").read_text(encoding="utf8")

    @property
    def content(self) -> bytes:
        return b"hello joaquim"

    @property
    def html(self) -> MockHTML:
        return MockHTML()

    def json(self) -> dict[str, Any]:
        return json.loads(Path("tests/samples/naruto.json").read_bytes())
