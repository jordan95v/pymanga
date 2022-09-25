import asyncio
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from zipfile import ZipFile
import httpx
from pydantic import BaseModel
from requests_html import AsyncHTMLSession, Element, HTMLResponse
from requests import HTTPError
from core.utils.exceptions import ChapterNotFound

__all__: list[str] = ["Chapter", "Manga"]


class Chapter(BaseModel):
    title: str | None = None
    link: str | None = None
    publication_date: datetime | None = None

    async def images_links(self) -> list[str]:
        """Get all the images link for a chapter, i know it use requests-html instead of
        httpx, but i had to in order to run the javascript.

        Args:
            url: Url of the chapter

        Return:
            list[str]: List of all the images links.
        """

        js_session: AsyncHTMLSession = AsyncHTMLSession()
        try:
            res: HTMLResponse = await js_session.get(self.link)
            res.raise_for_status()
        except HTTPError:
            raise ChapterNotFound()
        else:
            print(f"[SCRAPING] Retrieving images links for: {self.title}")
            await res.html.arender(timeout=0)  # Disable timeout, page able to load :)
            images: list[Element] = res.html.find(".img-fluid")
            await js_session.close()
            return sorted([element.attrs.get("src") for element in images])

    async def _call(
        self, url: str, client: httpx.AsyncClient, sem: asyncio.Semaphore
    ) -> httpx.Response:
        """Used to limits number of requests.

        Args:
            url: URL to request.
            client: The httpx session.
            sem: The semaphore used to limits number of request at the same time.

        Return
            httpx.Response: Response from the request.
        """

        async with sem:
            res: httpx.Response = await client.get(url)
        return res

    async def download_images(self, path: Path, *, limit: int = 10) -> Path:
        """Download the images into a zipfile for a chapter.

        Args:
            path: Path of the directory where the zip gonna be stored.
            limit: Number of images downloaded at the same time (if you got a slow
                connection, you might want a low number here).

        Return:
            Path: Path of the zipfile created.
        """

        images_links: list[str] = await self.images_links()
        print(f"[DOWNLOAD] Downloading images for: {self.title}")
        async with httpx.AsyncClient() as client:
            sem: asyncio.Semaphore = asyncio.Semaphore(limit)
            ret: list[httpx.Response] = await asyncio.gather(
                *[self._call(url, client, sem) for url in images_links]
            )
        output: Path = path / f"{self.title}.cbz"
        with ZipFile(output, "w") as zp:
            for url, res in zip(images_links, ret):
                zp.writestr(f"{url.rsplit('/')[-1]}", res.content)
        return output


class Manga(BaseModel):
    title: str | None = None
    link: str | None = None
    image: str | None = None
    chapters: list[Chapter] | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
