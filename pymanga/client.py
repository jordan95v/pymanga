import asyncio
import re
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import ClassVar, Type
from urllib.parse import urljoin
from zipfile import ZipFile
import httpx
import typer
from lxml import etree
from rich.progress_bar import ProgressBar
from rich.progress import track, Progress, TaskID
from pymanga.models import Chapter
from pymanga.utils.exceptions import MangaNotFound

__all__: list[str] = ["Client"]


@dataclass
class Client:
    base_url: ClassVar[str] = "https://mangasee123.com/"
    _session: httpx.AsyncClient = httpx.AsyncClient()

    async def _call(
        self,
        url: str,
        session: httpx.AsyncClient,
        sema: asyncio.Semaphore | None = None,
        progress: Progress | None = None,
    ) -> httpx.Response:
        """Make a request to a url.

        Args:
            url (str): Url to make the request to.

        Returns:
            Response: A response object.
        """

        await sema.acquire() if sema else None
        progress.console.print(f"Downloading {url}") if progress else None
        res: httpx.Response = await session.get(url)
        progress.update(progress.tasks[0].id, advance=1) if progress else None
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
        images_urls: list[str] = await chapter.get_images(self._session)

        with Progress() as progress:
            progress.add_task(
                "[bold green]Downloading...[/bold green]", total=len(images_urls)
            )
            res: list[httpx.Response] = await asyncio.gather(
                *[self._call(url, self._session, sema, progress) for url in images_urls]
            )

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

        pattern: re.Pattern[str] = re.compile(r"[^a-zA-Z0-9-]")
        res: httpx.Response = await self._call(
            urljoin(self.base_url, f"rss/{pattern.sub(' ', name)}.xml"), self._session
        )
        try:
            res.raise_for_status()
        except httpx.HTTPError:
            raise MangaNotFound(name)

        xml: etree._Element = etree.fromstring(res.text)
        return [
            Chapter(
                item.find("link").text.split("/")[-1].replace("-page-1.html", ""),
                item.find("link").text.replace("-page-1", ""),
            )
            for item in xml.findall(".//item")[::-1]
        ]

    async def close(self) -> None:
        """Close the client."""

        await self._session.aclose()

    async def __aenter__(self) -> "Client":
        """Enter the client.

        Returns:
            Client: The client object.
        """

        return self

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

        await self.close()
        if exc_type:
            raise exc_type(exc_val, exc_tb)
