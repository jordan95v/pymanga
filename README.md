<h1>pymanga</h1>

This is still a work in progress.

Hello everyone, `pymanga` is a simple manga downloader written in python. It scraps [mangasee](https://mangasee123.com/) and download any chapter you want.<br>
If you enjoy the content, be sure to check out the original website and obviously support the author.

<img src="https://media.tenor.com/Dx7Ek15cLFEAAAAC/bleach-anime.gif" width="100%">

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
from pymanga import Client

async def main() -> None:
    client = Client()
    # Do stuff with the client
```
This is going to impact performance a little bit, because it's going to create an `httpx.AsyncClient` for every request.

You can also pass a custom `httpx.AsyncClient` to the client, like this:
Be sure to call the `close` method of the client at the end of the program, or you will have a memory leak.

```python
import httpx
from pymanga import Client

async def main() -> None:
    client = Client(session=httpx.AsyncClient())
    # Do stuff with the client
    await client.close()
```

If you do not find a manga, please go on [mangasee](https://mangasee123.com/) and check if the manga is there.<br>
If it is, please go grab the manga's name in the RSS url and retry.

# Commands

`pymanga` comes with a command line interface, so you can use it like this:

```bash
(venv) $ python -m pymanga --help
```

That will show you all the available commands and options.

# Contributing

Contributions to `pymanga` are welcome! If you encounter any issues or have suggestions for improvements, please open an issue on the project's GitHub repository.<br>
Before submitting a pull request, make sure to run the tests and ensure that your changes do not break the existing functionality. Add tests for any new features or fixes you introduce.

# License

`pymanga` is open-source software released under the [MIT License](https://opensource.org/license/mit/). Feel free to use, modify, and distribute it according to the terms of the license.

# Acknowledgements

This project was developed by [jordan95v](https://github.com/jordan95v).<br>
I would like to thank the NewsAPI team for providing a powerful and comprehensive news service, making it easier for developers to integrate news data into their applications.

<h1>Thanks you for reading me and using <b>pymanga</b>!</h1>

<img src="https://media.tenor.com/pGx47sxMo4gAAAAC/bye-goodbye.gif" width="100%">
