import re

__all__: list[str] = ["CURRENT_CHAPTER_REGEX", "CHAPTER_PATH_REGEX"]

pattern: str
pattern = r"vm\.CurChapter\s*=\s*({[^}]*});"
CURRENT_CHAPTER_REGEX = re.compile(pattern, re.MULTILINE | re.DOTALL)

pattern = r'vm\.CurPathName\s*=\s*"(?P<CurPathName>[^"]*)";'
CHAPTER_PATH_REGEX = re.compile(pattern, re.MULTILINE | re.DOTALL)
