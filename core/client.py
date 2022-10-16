import asyncio
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import TracebackType
from typing import Any, Type
from zipfile import ZipFile
import httpx
from lxml import etree
from typing_extensions import Self
from core.models.manga import Chapter, Manga
from core.utils.exceptions import MangaNotFound, ParsingError

__all__: list[str] = ["Client"]


@dataclass
class Client:
    base_url: str = "https://mangasee123.com/rss/"
    session: httpx.AsyncClient = httpx.AsyncClient()

    async def _parse_xml(self, xml: etree._Element) -> dict[str, Any]:
        """Parse the XML from MangaSee and retrieve info.

        Args:
            xml: The XML to parse as lxml etree element.

        Return:
            Manga: The dataclass with extracted info.
        """

        try:
            link: str = xml.xpath("/rss/channel/link/text()")[0]
            title: str = " ".join(link.split("/")[-1].split("-"))
            image: str = xml.xpath("/rss/channel/image/url/text()")[0]
            chapters: list[Chapter] = [
                Chapter(
                    title=item.findtext("title"),
                    link=re.sub(r"-page-\d+", "", item.findtext("link")),
                    publication_date=datetime.strptime(
                        item.findtext("pubDate"), "%a, %d %b %Y %H:%M:%S %z"
                    ),
                )
                for item in xml.xpath("/rss/channel/item")[::-1]
            ]
        except IndexError:
            raise ParsingError()
        else:
            return dict(title=title, link=link, image=image, chapters=chapters)

    async def _get_info(self, name: str) -> dict[str, str]:
        try:
            res: httpx.Response = await self.session.get(
                f"https://kitsu.io/api/edge/manga",
                params={
                    "filter[text]": name,
                    "fields[manga]": "startDate,endDate,description",
                },
            )
            res.raise_for_status()
        except httpx.HTTPError:
            raise MangaNotFound()
        else:
            data: dict[str, Any] = res.json()["data"][0]["attributes"]
            return dict(
                description=data["description"],
                start_date=data["startDate"],
                end_date=data["endDate"],
            )

    async def get_manga_info(self, manga_name: str) -> Manga:
        """Get any scan info available on MangaSee RSS feed.

        Args:
            name: Name of the manga.

        Return:
            Manga: The dataclass with extracted info.
        """
        name: str = re.sub(r"[^\w]", " ", manga_name).replace("_", " ")
        try:
            res: httpx.Response = await self.session.get(
                f"{self.base_url}{'-'.join(name.split())}.xml"
            )
            res.raise_for_status()
        except httpx.HTTPError:
            raise MangaNotFound()
        else:
            rss_ret: dict[str, str] = await self._parse_xml(etree.fromstring(res.text))
            kitsu_res: dict[str, str] = await self._get_info(name)
            return Manga(**rss_ret, **kitsu_res)

    async def _call(self, url: str, sem: asyncio.Semaphore) -> httpx.Response:
        """Used to limits number of requests.

        Args:
            url: URL to request.
            sem: The semaphore used to limits number of request at the same time.

        Return
            httpx.Response: Response from the request.
        """

        async with sem:
            res: httpx.Response = await self.session.get(url)
        return res

    async def download_images(
        self, path: Path, chapter: Chapter, *, limit: int = 10
    ) -> Path:
        """Download the images into a zipfile for a chapter.

        Args:
            path: Path of the directory where the zip gonna be stored.
            limit: Number of images downloaded at the same time (if you got a slow
                connection, you might want a low number here).

        Return:
            Path: Path of the zipfile created.
        """

        images_links: list[str] = await chapter.images_links()
        print(f"[DOWNLOAD] Downloading images for: {chapter.title}")
        sem: asyncio.Semaphore = asyncio.Semaphore(limit)
        ret: list[httpx.Response] = await asyncio.gather(
            *[self._call(url, sem) for url in images_links]
        )
        output: Path = path / f"{chapter.title}.cbz"
        with ZipFile(output, "w") as zp:
            for url, res in zip(images_links, ret):
                zp.writestr(f"{url.rsplit('/')[-1]}", res.content)
        return output

    async def close(self) -> None:
        """Close the httpx and requests-html session."""

        await self.session.aclose()

    async def __aenter__(self) -> Self:
        """Context manager enter."""

        return self

    async def __aexit__(
        self,
        err_type: Type[Exception] | None,
        err_value: Exception | None,
        tb: TracebackType | None,
    ) -> None:
        """Context manager exit."""

        await self.close()
        if err_type:
            raise err_type(err_value)
