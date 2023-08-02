import asyncio

from core.models import Chapter
from .client import Client


async def _call(self, chapter: Chapter, semaphore: asyncio.Semaphore) -> list[str]:
    async with semaphore:
        print(f"Downloading {chapter.name}")
        return await chapter.get_images()


async def main() -> None:
    client: Client = Client()
    chapters: list[Chapter] = await client.get_chapters("bleach")
    print(chapters)


if __name__ == "__main__":
    asyncio.run(main())
