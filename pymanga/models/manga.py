from dataclasses import dataclass
import json
from pathlib import Path
import re
import httpx
from pymanga.utils.exceptions import ChapterNotFound
from pymanga.utils.regex import CURRENT_CHAPTER_REGEX, CHAPTER_PATH_REGEX

__all__: list[str] = ["Chapter"]


@dataclass
class Chapter:
    name: str
    url: str

    async def get_images(self, session: httpx.AsyncClient) -> list[str]:
        res: httpx.Response = await session.get(self.url)
        try:
            res.raise_for_status()
        except httpx.HTTPError:
            raise ChapterNotFound(f"Chapter {self.name} not found")

        match: re.Match[str] | None
        if match := CURRENT_CHAPTER_REGEX.search(res.text):
            info: dict[str, str] = json.loads(match.group(1))
            directory: str = info.get("Directory", "")
            page: int = int(info.get("Page", 0))
        if match := CHAPTER_PATH_REGEX.search(res.text):
            base_image_url: str = match.group("CurPathName")

        urls: list[str] = []
        for i in range(1, page + 1):
            number_path: str = (
                f"{self.number:04}-{i:03}"
                if isinstance(self.number, int)
                else f"{self.number:06.1f}-{i:03}"
            )
            path: str = f"{directory + '/' if directory else ''}{number_path}.png"
            urls.append(f"https://{base_image_url}/manga/{self.slug}/{path}")
        return urls

    @property
    def slug(self) -> str:
        slug: list[str] = []
        for word in self.name.split():
            if "chapter" in word.lower():
                break
            slug.append(word.title())
        return "-".join(slug)

    @property
    def number(self) -> float | int:
        number: str = self.name.split()[-1]
        if number.isnumeric():
            return int(number)
        return float(number)
