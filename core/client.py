from dataclasses import dataclass
from pathlib import Path
from typing import Any
from datetime import datetime
import httpx
import re
from lxml import etree
from core.models.manga import Chapter, Manga

__all__: list[str] = ["Client"]


@dataclass
class Client:
    base_url: str = "https://mangasee123.com/rss/"

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

        async with httpx.AsyncClient() as client:
            res: httpx.Response = await client.get(
                f"{self.base_url}{'-'.join(name.split())}.xml"
            )
            try:
                res.raise_for_status()
            except httpx.HTTPError:
                print("[ERROR] Request ended in 404 error.")
            else:
                try:
                    xml: etree._Element = etree.fromstring(res.text)
                    return await self._parse_xml(xml)
                except etree.XMLSyntaxError:
                    print("[ERROR] Bad XML, cannot parse.")
