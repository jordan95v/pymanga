from typing import Any, Type
import pytest
from pytest_mock import MockerFixture
from requests_html import AsyncHTMLSession
from conftest import MockHTMLResponse
from pymanga.models import Chapter
from pymanga.utils.exceptions import ChapterNotFound


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
