from datetime import date, datetime
from core.utils.exceptions import ChapterNotFound
from pydantic import BaseModel
from requests import HTTPError
from requests_html import AsyncHTMLSession, Element, HTMLResponse

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


class Manga(BaseModel):
    title: str | None = None
    link: str | None = None
    image: str | None = None
    chapters: list[Chapter] | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
