import asyncio
from pathlib import Path
from typing import Union
import typer
from rich import print
from typing_extensions import Annotated
from pymanga.client import Client
from pymanga.models import Chapter

app: typer.Typer = typer.Typer()


@app.command()
def main(
    manga_name: Annotated[str, typer.Argument(help="Name of the manga.")],
    output: Annotated[Path, typer.Option(help="Output directory.")] = Path.cwd(),
    from_: Annotated[
        Union[int, None],
        typer.Argument(
            help="Download from this chapter.", rich_help_panel="Secondary arguments"
        ),
    ] = None,
    to: Annotated[
        Union[int, None],
        typer.Argument(
            help="End download to this chapter.", rich_help_panel="Secondary arguments"
        ),
    ] = None,
) -> None:
    async def handle(
        manga_name: str, output: Path, from_: int | None, to: int | None
    ) -> None:
        async with Client() as client:
            chapters: list[Chapter] = await client.get_chapters(manga_name)
            if from_ is not None and to is not None:
                chapters = chapters[from_ - 1 : to]
            elif from_ is not None:
                chapters = chapters[from_ - 1 :]
            print(f"Downloading [green]{len(chapters)}[/green] chapters ...\n")

            for chapter in chapters:
                print(f"[bold]Downloading[/bold] [blue]{chapter.name}[/blue]")
                await client.download_chapter(chapter, output, 3)
                print(
                    f"[bold green]Downloaded[/bold green]"
                    f" [blue]{chapter.name}[/blue] to [yellow]{output}[/yellow] !\n"
                )

    asyncio.run(handle(manga_name, output, from_, to))


if __name__ == "__main__":
    app()
