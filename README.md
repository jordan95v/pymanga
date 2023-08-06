<h1>pymanga</h1>

This is still a work in progress.

Hello everyone, `pymanga` is a simple manga downloader written in python. It scraps [mangasee](https://mangasee123.com/) and download any chapter you want.<br>
If you enjoy the content, be sure to check out the original website and obviously support the author.

<img src="https://media.tenor.com/Dx7Ek15cLFEAAAAC/bleach-anime.gif" width="100%">

<h1>Table of contents</h1>

- [Code structure](#code-structure)
- [Installation](#installation)
- [Usage](#usage)
  - [Get manga chapters](#get-manga-chapters)
  - [Download a chapter](#download-a-chapter)
- [Commands](#commands)
- [Docker](#docker)
- [Contributing](#contributing)
- [License](#license)

# Code structure

`pymanga` is a simple project, so the code structure is pretty simple too.

```bash
├── pymanga
│   ├── models
│   │   ├── __init__.py
│   │   ├── manga.py # Contains the Chapter class.
│   ├── utils
│   │   ├── __init__.py
│   │   ├── exceptions.py # Contains all the exceptions used by client.
│   │   ├── regex.py # Contains regex to scrap the website.
│   ├── __init__.py
│   ├── __main__.py
│   ├── client.py
```

# Installation

```bash
$ python -m venv venv
$ source venv/bin/activate # ven\Scripts\activate on Windows
(venv) $ pip install . # .[dev] for development
```

And you're set to go 🤩

# Usage

`pymanga` have a client that implement a context manager, so you can use it like this:

```python
from pymanga import Client

async def main() -> None:
    async with Client() as client:
        # Do stuff with the client
```

This is because the http session needs to be closed at the end of the program, so the context manager will take care of that for you.
However, if you want to use the client outside of a context manager, you can do it like this:

```python
import httpx
from pymanga import Client

async def main() -> None:
    client = Client(session=httpx.AsyncClient())
    # Do stuff with the client
    await client.close()
```

Be sure to call the `close` method of the client at the end of the program, or you will have a memory leak.

If you do not find a manga, please go on [mangasee](https://mangasee123.com/) and check if the manga is there.<br>
If it is, please go grab the manga's name in the RSS url and retry.

## Get manga chapters

The client comes with `get_chapters` method that returns a list of `Chapter` objects.

```python
from pymanga import Client

async def main() -> None:
    async with Client() as client:
        chapters = await client.get_chapters("bleach")
        print(chapters)
```

## Download a chapter

The client comes with a `download_chapter` method that will download the chapter in the current directory.
The method takes a `Chapter` object as argument. I made it in the client to unify the http session used.

```python
from pathlib import Path
from pymanga import Client

async def main() -> None:
    async with Client() as client:
        chapters = await client.get_chapters("bleach")
        output: Path = Path.cwd() / "bleach"
        limit: int = 10 # Limit the number of images downloaded concurrently
        await client.download_chapter(chapters[0], output, limit)
```

# Commands

`pymanga` comes with a command line interface, so you can use it like this:

```bash
(venv) $ python -m pymanga --help

# Download chapters 2 to 5 of Bleach in ./pymanga-output directory
(venv) $ python -m pymanga Bleach 2 5 --output ./pymanga-output
```

That will show you all the available commands and options.

# Docker

`pymanga` also comes with docker implementation.

```bash
$ docker compose up

# Download chapters 2 to 5 of Bleach
$ docker exec pymanga python -m pymanga Bleach 2 5 --output /app/output
```

`/app/output` is linked to your local directory `./output` that was created with the first docker command.

# Contributing

Contributions to `pymanga` are welcome! If you encounter any issues or have suggestions for improvements, please open an issue on the project's GitHub repository.<br>
Before submitting a pull request, make sure to run the tests and ensure that your changes do not break the existing functionality. Add tests for any new features or fixes you introduce.

# License

`pymanga` is open-source software released under the [MIT License](https://opensource.org/license/mit/). Feel free to use, modify, and distribute it according to the terms of the license.

<h1>Thanks you for reading me and using <b>pymanga</b>!</h1>

<img src="https://media.tenor.com/pGx47sxMo4gAAAAC/bye-goodbye.gif" width="100%">
