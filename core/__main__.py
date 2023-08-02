import asyncio
from .client import Client


async def main() -> None:
    client: Client = Client()
    async for chapter in client.get_chapters("bleach"):
        print(chapter)


if __name__ == "__main__":
    asyncio.run(main())
