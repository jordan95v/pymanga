from typing import AsyncGenerator, ClassVar
from urllib.parse import urljoin
import httpx
from lxml import etree
from core.models import Chapter
from core.utils.exceptions import MangaNotFound


class Client:
    base_url: ClassVar[str] = "https://mangasee123.com/"

    async def get_chapters(self, name: str) -> list[Chapter]:
        """Get chapters of a manga.

        Args:
            name (str): Name of the manga.

        Raises:
            MangaNotFound: If the manga is not found.

        Returns:
            AsyncGenerator[Chapter, None]: An async generator of chapters.
        """

        async with httpx.AsyncClient() as client:
            res: httpx.Response = await client.get(
                urljoin(self.base_url, f"rss/{'-'.join(name.title().split())}.xml")
            )
        try:
            res.raise_for_status()
        except httpx.HTTPError:
            raise MangaNotFound(name)

        xml: etree._Element = etree.fromstring(res.text)

        return [
            Chapter(
                item.find("title").text.strip(),
                item.find("link").text.replace("-page-1", ""),
            )
            for item in xml.findall(".//item")[::-1]
        ]
