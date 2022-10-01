import asyncio
from pathlib import Path
import click
from core.client import Client
from core.models.manga import Chapter, Manga
from core.utils.exceptions import MangaNotFound


async def dl_chapter(
    chapter: Chapter, path: Path, client: Client, sem: asyncio.Semaphore
) -> None:
    async with sem:
        await client.download_images(path, chapter, limit=5)


async def scrap_chapter(name: str, chp_num: str, path: Path) -> None:
    async with Client() as client:
        try:
            manga: Manga = await client.get_manga_info(name)  # type: ignore
        except MangaNotFound:
            print(f'"{name} not found.')
        else:
            for chapter in manga.chapters:  # type: ignore
                if chp_num in chapter.title:  # type: ignore
                    await client.download_images(path, chapter)  # type: ignore
                    break


async def scrap(name: str, path: Path, limit: int) -> None:
    async with Client() as client:
        try:
            manga: Manga = await client.get_manga_info(name)  # type: ignore
        except MangaNotFound:
            print(f'"{name} not found.')
        else:
            manga_dir: Path = path / name
            manga_dir.mkdir(exist_ok=True)
            sem: asyncio.Semaphore = asyncio.Semaphore(limit)
            await asyncio.gather(
                *[
                    dl_chapter(chapter, manga_dir, client, sem)
                    for chapter in manga.chapters  # type: ignore
                    if (manga_dir / f"{chapter.title}.cbz") not in manga_dir.iterdir()
                ]
            )


@click.command()
@click.option(
    "--name", prompt="Enter the manga name", type=str, help="Name of the manga."
)
@click.option(
    "--path",
    prompt="Enter the path of stored files",
    type=Path,
    help="Path of futur stored scan.",
    default=(Path.home() / "Desktop"),
)
@click.option("--chp_num", prompt="Enter the chapter's number", type=str)
def download_chapter(name: str, path: Path, chp_num: str):
    asyncio.run(scrap_chapter(name, chp_num, path))


@click.command()
@click.option(
    "--name", prompt="Enter the manga name", type=str, help="Name of the manga."
)
@click.option(
    "--path",
    prompt="Path of stored files",
    type=Path,
    help="Path of futur stored scan.",
    default=(Path.home() / "Desktop"),
)
@click.option(
    "--limit", prompt="Limit of chapter downloaded concurently", type=int, default=5
)
def download_all(name: str, path: Path, limit: int):
    asyncio.run(scrap(name, path, limit))


@click.group()
def main():
    pass


if __name__ == "__main__":
    main.add_command(download_chapter)
    main.add_command(download_all)
    main()
