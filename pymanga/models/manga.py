import json
import posixpath
import re
from dataclasses import dataclass
from urllib.parse import urljoin
import httpx
from pymanga.utils.exceptions import ChapterNotFound, ChapterError
from pymanga.utils.regex import CHAPTER_PATH_REGEX, CURRENT_CHAPTER_REGEX

__all__: list[str] = ["Chapter"]


@dataclass
class Chapter:
    name: str
    url: str

    async def _parse_html(self, res: httpx.Response) -> tuple[int, str, str]:
        """Parse the html to get the page, directory and base image url.

        Args:
            res (httpx.Response): The response to parse.

        Raises:
            ChapterError: If an error happens while parsing the html.

        Returns:
            tuple[int, str, str]: The page, directory and base image url.
        """

        page: int = 0
        directory: str = ""
        base_image_url: str = ""

        match: re.Match[str] | None
        if match := CURRENT_CHAPTER_REGEX.search(res.text):
            try:
                info: dict[str, str] = json.loads(match.group(1))
            except json.JSONDecodeError:
                raise ChapterError("Error while parsing chapter info")
            else:
                directory = info.get("Directory", "")
                page = int(info.get("Page", 0))

        if match := CHAPTER_PATH_REGEX.search(res.text):
            base_image_url = match.group("CurPathName")
        else:
            raise ChapterError("Error while parsing chapter info")

        return page, directory, base_image_url

    def _get_number_path(self, number: int) -> str:
        """Construct the path of the image.

        Args:
            number (int): The number of the image.

        Returns:
            str: The constructed path of the image.
        """

        chapter_number: str = self.name.split("-")[-1]

        return (
            f"{float(chapter_number):06.1f}-{number:03}.png"
            if not chapter_number.isnumeric()
            else f"{int(chapter_number):04}-{number:03}.png"
        )

    async def get_images(self, session: httpx.AsyncClient) -> list[str]:
        """Get the images of a chapter.

        Args:
            session (httpx.AsyncClient): The session to use.

        Raises:
            ChapterNotFound: If the chapter is not found.

        Returns:
            list[str]: The list of images.
        """

        res: httpx.Response = await session.get(self.url)
        try:
            res.raise_for_status()
        except httpx.HTTPError:
            raise ChapterNotFound(f"Chapter {self.name} not found")

        # i don't know how to type hint these variables without it looking ugly
        page, directory, base_image_url = await self._parse_html(res)
        base_chapter_url: str = f"https://{base_image_url}/manga/{self.slug}"
        return [
            f"{posixpath.join(base_chapter_url, directory, self._get_number_path(i))}"
            for i in range(1, page + 1)
        ]

    @property
    def slug(self) -> str:
        """Get the slug of the chapter."""

        slug: list[str] = []
        for word in self.name.split("-"):
            if "chapter" in word.lower():
                break
            slug.append(word)
        return "-".join(slug)
