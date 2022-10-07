import asyncio
from pathlib import Path
import typer
from core.client import Client
from core.models.manga import Chapter, Manga
from core.utils.exceptions import MangaNotFound

app: typer.Typer = typer.Typer()


async def _dl_chapter(
    chapter: Chapter, path: Path, client: Client, sem: asyncio.Semaphore
) -> None:
    async with sem:
        await client.download_images(path, chapter, limit=5)


async def scrap_chapter(name: str, chapter_num: str, path: Path) -> None:
    async with Client() as client:
        try:
            manga: Manga = await client.get_manga_info(name)  # type: ignore
        except MangaNotFound:
            print(f"{name} not found.")
        else:
            for chapter in manga.chapters:  # type: ignore
                if chapter_num in chapter.title:  # type: ignore
                    await client.download_images(path, chapter)  # type: ignore
                    break


async def scrap(name: str, path: Path, limit: int) -> None:
    async with Client() as client:
        try:
            manga: Manga = await client.get_manga_info(name)  # type: ignore
        except MangaNotFound:
            print(f"{name} not found.")
        else:
            manga_dir: Path = path / name
            manga_dir.mkdir(exist_ok=True)
            sem: asyncio.Semaphore = asyncio.Semaphore(limit)
            await asyncio.gather(
                *[
                    _dl_chapter(chapter, manga_dir, client, sem)
                    for chapter in manga.chapters  # type: ignore
                    if (manga_dir / f"{chapter.title}.cbz") not in manga_dir.iterdir()
                ]
            )


@app.command()
def dl_all():
    name: str = typer.prompt("Enter the mange name", type=str)
    path: str = typer.prompt(
        "Enter the path of stored scan", default=Path().home(), type=Path
    )
    limit: str = typer.prompt(
        "Enter le limit of chapter downloaded at the same time", type=int, default=5
    )
    asyncio.run(scrap(name, path, limit))


@app.command()
def dl_chapter():
    name: str = typer.prompt("Enter the mange name", type=str)
    chapter_num: str = typer.prompt("Enter the chapter number", type=str)
    path: str = typer.prompt(
        "Enter the path of stored scan", default=Path().home(), type=Path
    )
    asyncio.run(scrap_chapter(name, chapter_num, path))


if __name__ == "__main__":
    app()
