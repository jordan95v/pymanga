from dataclasses import dataclass
from requests import HTTPError
from requests_html import AsyncHTMLSession, HTMLResponse
from core.utils.exceptions import ChapterNotFound

__all__: list[str] = ["Chapter"]


@dataclass
class Chapter:
    name: str
    url: str

    async def get_images(self, session: AsyncHTMLSession) -> list[str]:
        res: HTMLResponse = await session.get(self.url)
        try:
            res.raise_for_status()
        except HTTPError:
            raise ChapterNotFound(f"Chapter {self.name} not found")
        await res.html.arender(timeout=0, sleep=1)
        return [element.attrs.get("src", "") for element in res.html.find(".img-fluid")]
