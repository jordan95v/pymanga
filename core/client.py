import re
from dataclasses import dataclass
from datetime import datetime
import httpx
import requests_html
from requests import HTTPError
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
                print("[ERROR] Provided URL resulted in a 404 error.")
            else:
                try:
                    xml: etree._Element = etree.fromstring(res.text)
                    return await self._parse_xml(xml)
                except etree.XMLSyntaxError:
                    print("[ERROR] Cannot parse provided XML.")

    async def get_chapter_image(self, url: str) -> list[str]:
        """Get all the images link for a chapter, i know it use requests instead of
        httpx, but i had to in order to run the javascript.

        Args:
            url: Url of the chpater

        Return:
            list[str]: List of all the images links.
        """

        session: requests_html.AsyncHTMLSession = requests_html.AsyncHTMLSession()
        try:
            res: requests_html.HTMLResponse = await session.get(url)
            res.raise_for_status()
        except HTTPError:
            print("[ERROR] Provided URL resulted in a 404 error.")
        else:
            await res.html.arender(timeout=60)
            images: list[requests_html.Element] = res.html.find(".img-fluid")
            print(images)
            await session.close()
            return sorted([element.attrs.get("src") for element in images])
