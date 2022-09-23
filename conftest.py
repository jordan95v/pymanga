from dataclasses import dataclass
from pathlib import Path
from typing import Any
import httpx
from requests import HTTPError


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
            raise httpx.HTTPError("Error")
        elif self.status_code == 401:
            raise HTTPError

    @property
    def text(self) -> str:
        if self.status_code != 200:
            return "holla, the xml parser cannot parse me bhahahaha"
        else:
            return Path("tests/samples/naruto.xml").read_text(encoding="utf8")

    @property
    def html(self) -> MockHTML:
        return MockHTML()
