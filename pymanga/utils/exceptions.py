class MangaNotFound(Exception):
    """Raised when a manga is not found."""


class ChapterNotFound(Exception):
    """Raised when a chapter is not found."""


class ChapterError(Exception):
    """Raised when an error happens when gathering images for chapter."""
