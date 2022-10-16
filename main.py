import asyncio
import enum
from pathlib import Path
from typing import Any
import typer
from core.client import Client
from core.models.manga import Chapter, Manga
from core.utils.exceptions import MangaNotFound


class Mode(enum.Enum):
    DL_ALL: enum.auto = enum.auto()
    DL_CHAPTER: enum.auto = enum.auto()


app: typer.Typer = typer.Typer()


async def ask_user(mode: Mode) -> Any:
    name: str = typer.prompt("Enter the mange name", type=str)
    path: str = typer.prompt(
        "Enter the path of stored scan", default=Path().home(), type=Path
    )
    if mode == Mode.DL_ALL:
        limit: str = typer.prompt(
            "Enter the limit of chapter downloaded at the same time",
            type=int,
            default=5,
        )
        return name, path, limit
    else:
        chapter_num: str = typer.prompt("Enter the chapter number", type=str)
        return name, chapter_num, path


async def _dl_chapter(
    chapter: Chapter, path: Path, client: Client, sem: asyncio.Semaphore
) -> None:
    async with sem:
        await client.download_images(path, chapter, limit=5)


async def scrap_chapter() -> None:
    name: str
    chapter_num: str
    path: Path
    name, chapter_num, path = await ask_user(Mode.DL_CHAPTER)
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


async def scrap() -> None:
    name: str
    path: Path
    limit: int
    name, path, limit = await ask_user(Mode.DL_ALL)
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
    asyncio.run(scrap())


@app.command()
def dl_chapter():
    asyncio.run(scrap_chapter())


if __name__ == "__main__":
    app()
