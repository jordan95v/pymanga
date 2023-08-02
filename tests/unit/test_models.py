from dataclasses import dataclass
from typing import Any, Type
import pytest
from pytest_mock import MockerFixture
from requests import HTTPError
from requests_html import AsyncHTMLSession
from core.models import Chapter
from core.utils.exceptions import ChapterNotFound


@pytest.fixture
def chapter() -> Chapter:
    return Chapter(name="fake_chapter", url="https://fake_url.com")


class MockElement:
    @property
    def attrs(self) -> dict[str, Any]:
        return {"src": "https://fake_url.com"}


class HTMLMock:
    async def arender(self, *args: Any, **kwargs: Any) -> None:
        pass

    def find(self, *args: Any, **kwargs: Any) -> list[MockElement]:
        return [MockElement() for _ in range(2)]


@dataclass
class MockHTMLResponse:
    status_code: int

    @property
    def html(self) -> HTMLMock:
        return HTMLMock()

    def raise_for_status(self) -> None:
        if self.status_code != 200:
            raise HTTPError("fake_error")


@pytest.mark.asyncio
class TestChapter:
    @pytest.mark.parametrize(
        "status_code, throwable",
        [
            (200, False),
            (404, ChapterNotFound),
        ],
    )
    async def test_get_images(
        self,
        chapter: Chapter,
        mocker: MockerFixture,
        status_code: int,
        throwable: Type[Exception],
    ) -> None:
        async def patch_html(*args: Any, **kwargs: Any) -> MockHTMLResponse:
            return MockHTMLResponse(status_code)

        mocker.patch.object(AsyncHTMLSession, "get", patch_html)
        session: AsyncHTMLSession = AsyncHTMLSession()

        if throwable:
            with pytest.raises(throwable):
                await chapter.get_images(session)
            await session.close()
        else:
            imgs: list[str] = await chapter.get_images(session)
            await session.close()
            assert imgs == ["https://fake_url.com" for _ in range(2)]
