from dataclasses import dataclass
from pathlib import Path
from lxml import etree
import httpx


@dataclass
class MockResponse:
    status_code: int

    def raise_for_status(self):
        if self.status_code != 200 and self.status_code != 415:
            raise httpx.HTTPError("Error")

    @property
    def text(self) -> str:
        if self.status_code != 200:
            return "holla, the xml parser cannot parse me bhahahaha"
        else:
            return Path("tests/samples/naruto.xml").read_text(encoding="utf8")
