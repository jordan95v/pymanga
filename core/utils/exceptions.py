class MangaNotFound(Exception):
    """Happens when the manga cannot be found on the website."""


class ChapterNotFound(Exception):
    """Happens when the chapter cannot be found on the website."""


class ParsingError(Exception):
    """Happens when the XML cannot be parsed (should not happen normally)."""
