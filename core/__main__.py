import asyncio
from pathlib import Path
from core.client import Client
from core.models.manga import Chapter


async def main() -> None:
    async with Client() as client:
        chapters: list[Chapter] = await client.get_chapters("bleach")
        await client.download_chapter(chapters[258], Path("output"), 5)


if __name__ == "__main__":
    asyncio.run(main())
