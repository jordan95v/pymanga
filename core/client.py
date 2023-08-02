from typing import AsyncGenerator, ClassVar
from urllib.parse import urljoin
import httpx
from lxml import etree
from core.models import Chapter


class Client:
    base_url: ClassVar[str] = "https://mangasee123.com/"

    async def get_chapters(self, name: str) -> AsyncGenerator[Chapter, None]:
        async with httpx.AsyncClient() as client:
            res: httpx.Response = await client.get(
                urljoin(self.base_url, f"rss/{'-'.join(name.title().split())}.xml")
            )
        xml: etree._Element = etree.fromstring(res.text)
        for item in xml.findall(".//item")[::-1]:
            yield Chapter(
                item.find("title").text.strip(),
                item.find("link").text.replace("-page-1", ""),
            )
