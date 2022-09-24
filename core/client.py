import asyncio
from pathlib import Path
import re
from dataclasses import dataclass
from datetime import datetime
from types import TracebackType
from typing import Type
from typing_extensions import Self
import httpx
from requests_html import AsyncHTMLSession, Element, HTMLResponse
from requests import HTTPError
from lxml import etree
from core.models.manga import Chapter, Manga
from core.utils.exceptions import ChapterNotFound, MangaNotFound

__all__: list[str] = ["Client"]


@dataclass
class Client:
    base_url: str = "https://mangasee123.com/rss/"
    session: httpx.AsyncClient = httpx.AsyncClient()

    async def _parse_xml(self, xml: etree._Element) -> Manga:
        """Parse the XML from MangaSee and retrieve info.

        Args:
            xml: The XML to parse as lxml etree element.

        Return:
            Manga: The dataclass with extracted info.
        """

        link: str = xml.xpath("/rss/channel/link/text()")[0]
        title: str = " ".join(link.split("/")[-1].split("-"))
        image: str = xml.xpath("/rss/channel/image/url/text()")[0]
        items: list[etree._Element] = xml.xpath("/rss/channel/item")
        chapters: list[Chapter] = [
            Chapter(
                title=item.findtext("title"),
                link=re.sub(r"-page-\d+", "", item.findtext("link")),
                publication_date=datetime.strptime(
                    item.findtext("pubDate"), "%a, %d %b %Y %H:%M:%S %z"
                ),
            )
            for item in items
        ]
        return Manga(title=title, link=link, image=image, chapters=chapters[::-1])

    async def get_manga_info(self, name: str) -> Manga:
        """Get any scan info available on MangaSee RSS feed.

        Args:
            name: Name of the manga.

        Return:
            Manga: The dataclass with extracted info.
        """

        res: httpx.Response = await self.session.get(
            f"{self.base_url}{'-'.join(name.split())}.xml"
        )
        try:
            res.raise_for_status()
        except httpx.HTTPError:
            raise MangaNotFound()
        else:
            xml: etree._Element = etree.fromstring(res.text)
            return await self._parse_xml(xml)

    async def close(self) -> None:
        """Close the httpx and requests-html session."""

        await self.session.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        err_type: Type[Exception] | None,
        err_value: Exception | None,
        tb: TracebackType | None,
    ) -> None:
        await self.close()
        if err_type:
            raise err_type(err_value)
