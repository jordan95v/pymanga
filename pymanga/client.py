import asyncio
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import ClassVar, Type
from urllib.parse import urljoin
from zipfile import ZipFile
from lxml import etree
from requests import HTTPError, Response
from requests_html import AsyncHTMLSession
from pymanga.models import Chapter
from pymanga.utils.exceptions import MangaNotFound

__all__: list[str] = ["Client"]


@dataclass
class Client:
    base_url: ClassVar[str] = "https://mangasee123.com/"
    session: AsyncHTMLSession | None = None

    async def _call(
        self, url: str, session: AsyncHTMLSession, sema: asyncio.Semaphore | None = None
    ) -> Response:
        """Make a request to a url.

        Args:
            url (str): Url to make the request to.

        Returns:
            Response: A response object.
        """

        await sema.acquire() if sema else None
        res: Response = await session.get(url)
        sema.release() if sema else None
        return res

    async def download_chapter(
        self, chapter: Chapter, output: Path, limit: int
    ) -> None:
        """Download a chapter.

        Args:
            chapter (Chapter): The chapter to download.
            output (Path): The output path.
            limit (int): The limit of concurrent image to downloads.
        """

        sema: asyncio.Semaphore = asyncio.Semaphore(limit)
        session: AsyncHTMLSession = self.session or AsyncHTMLSession()
        images_urls: list[str] = await chapter.get_images(session)
        res: list[Response] = await asyncio.gather(
            *[self._call(url, session, sema) for url in images_urls]
        )
        if not self.session:
            await session.close()

        output.mkdir(parents=True, exist_ok=True)
        with ZipFile(output / f"{chapter.name}.cbz", "w") as zip_file:
            for url, ret in zip(images_urls, res):
                image_name: str = url.split("/")[-1]
                zip_file.writestr(image_name, ret.content)

    async def get_chapters(self, name: str) -> list[Chapter]:
        """Get chapters of a manga.

        Args:
            name (str): Name of the manga.

        Raises:
            MangaNotFound: If the manga is not found.

        Returns:
            AsyncGenerator[Chapter, None]: An async generator of chapters.
        """

        session: AsyncHTMLSession = self.session or AsyncHTMLSession()
        res: Response = await self._call(
            urljoin(self.base_url, f"rss/{name.title().replace(' ', '-')}.xml"), session
        )
        try:
            res.raise_for_status()
        except HTTPError:
            raise MangaNotFound(name)
        if not self.session:
            await session.close()

        xml: etree._Element = etree.fromstring(res.text)
        return [
            Chapter(
                item.find("title").text.strip(),
                item.find("link").text.replace("-page-1", ""),
            )
            for item in xml.findall(".//item")[::-1]
        ]

    async def __aenter__(self) -> "Client":
        """Enter the client.

        Returns:
            Client: The client object.
        """

        self.session = AsyncHTMLSession()
        return self

    async def close(self) -> None:
        if self.session:
            await self.session.close()

    async def __aexit__(
        self,
        exc_type: Type[Exception] | None,
        exc_val: Exception | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the client.

        Args:
            exc_type ([type]): [description]
            exc_val ([type]): [description]
            exc_tb ([type]): [description]
        """

        if exc_type:
            await self.close()
            raise exc_type(exc_val, exc_tb)
        await self.close()
