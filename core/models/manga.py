import asyncio
from dataclasses import dataclass
from datetime import datetime
import functools
from pathlib import Path
from zipfile import ZipFile
import httpx
from requests_html import AsyncHTMLSession, Element, HTMLResponse
from requests import HTTPError
from core.utils.exceptions import ChapterNotFound

__all__: list[str] = ["Chapter", "Manga"]


@dataclass
class Chapter:
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
            print(f"[WORKING] Retrieving images links for: {self.link}")
            await res.html.arender(timeout=0)  # Disable timeout, page able to load :)
            images: list[Element] = res.html.find(".img-fluid")
            await js_session.close()
            return sorted([element.attrs.get("src") for element in images])

    async def download_images(self, path: Path) -> Path:
        images_links: list[str] = await self.images_links()
        async with httpx.AsyncClient() as client:
            ret: list[httpx.Response] = await asyncio.gather(
                *[client.get(url) for url in images_links]
            )
        output: Path = path / f"{self.title}.zip"
        with ZipFile(output, "w") as zp:
            for url, res in zip(images_links, ret):
                zp.writestr(f"{url.rsplit('/')[-1]}", res.content)
        return output


@dataclass
class Manga:
    title: str | None = None
    link: str | None = None
    image: str | None = None
    chapters: list[Chapter] | None = None
