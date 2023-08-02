from dataclasses import dataclass
from types import TracebackType
from typing import ClassVar, Type
from urllib.parse import urljoin
from lxml import etree
from requests import HTTPError, Response
from requests_html import AsyncHTMLSession
from core.models import Chapter
from core.utils.exceptions import MangaNotFound

__all__: list[str] = ["Client"]


@dataclass
class Client:
    base_url: ClassVar[str] = "https://mangasee123.com/"
    session: AsyncHTMLSession | None = None

    async def _call(self, url: str) -> Response:
        """Make a request to a url.

        Args:
            url (str): Url to make the request to.

        Returns:
            Response: A response object.
        """

        session: AsyncHTMLSession = self.session or AsyncHTMLSession()
        res: Response = await session.get(url)
        if not self.session:
            await session.close()
        return res

    async def get_chapters(self, name: str) -> list[Chapter]:
        """Get chapters of a manga.

        Args:
            name (str): Name of the manga.

        Raises:
            MangaNotFound: If the manga is not found.

        Returns:
            AsyncGenerator[Chapter, None]: An async generator of chapters.
        """

        res: Response = await self._call(urljoin(self.base_url, name))
        try:
            res.raise_for_status()
        except HTTPError:
            raise MangaNotFound(name)

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
