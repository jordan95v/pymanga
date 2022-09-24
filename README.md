# MANGA SCRAPER

Hey ! This is a little project i made in order to scrap the RSS feed from [MangaSee](https://mangasee123.com/).
It also allows you to download the scan 😎

- [MANGA SCRAPER](#manga-scraper)
  - [Installation](#installation)
  - [Workflow](#workflow)
    - [Get manga info](#get-manga-info)
    - [Download chapter images](#download-chapter-images)


## Installation

If you feel like the project needs something more, feel free to pull and dev ! Here's how to (but i guess you already know how to do) !

```shell
C:/Users/you> git clone https://www.github.com/jordan95v/manga_scraper
C:/Users/you> cd manga_scraper
C:/Users/you/manga_scraper> py -m venv venv
C:/Users/you/manga_scraper> venv/Scripts/activate # venv\bin\activate on Mac
(venv) C:/Users/you/manga_scraper> pip install -r requirements.txt -r requirements-dev.txt
```

And you're set to go !

## Workflow

So you ever wanted to download scan from [MangaSee](https://mangasee123.com/) ? I got you 🤩 !

### Get manga info

In order to download a chapter, you first needs to get the information of the manga from the RSS feed.

```python
import asyncio
from core.client import Client
from core.models.manga import Manga


async def main() -> None:
    async with Client() as client:
        res: Manga = await client.get_manga_info("Naruto")
        print(res.title) # Naruto

if __name__ == "__main__":
    asyncio.run(main())
```

### Download chapter images

Now that we got our hand on the manga's info, we can download the chapters.
It will come in the form of a zipfile.

```python
import asyncio
from core.client import Client
from core.models.manga import Manga


async def main() -> None:
    async with Client() as client:
        res: Manga = await client.get_manga_info("One Piece")
        output: Path = Path('One Piece')
        output.mkdir(exists_ok = True)
        await res.chapters[0].download_images(output, limit=25)

if __name__ == "__main__":
    asyncio.run(main())
```

⚠️ The parameter `limit` is here to limit the number of connections. 
If you download too much images at the same time, your connection might not be enought and the script will raise an error ! ⚠️
