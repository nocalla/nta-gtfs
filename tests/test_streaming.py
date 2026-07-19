"""Unit tests for nta_gtfs._streaming.download_zip_to_tempfile.

Regression coverage for issue #39: a dropped/stalled connection mid-download
can yield a truncated body without aiohttp raising ClientError, so the
truncated temp file was silently returned as if it downloaded successfully.
"""

from collections.abc import AsyncIterator
from unittest.mock import AsyncMock, MagicMock

import pytest

from nta_gtfs._streaming import download_zip_to_tempfile
from nta_gtfs.exceptions import StaticGtfsLoadError

_DUMMY_URL = "https://example.com/gtfs.zip"


def _make_truncated_session(*, declared_length: int, actual_body: bytes) -> MagicMock:
    """Return a mock session whose response under-delivers its Content-Length.

    Args:
        declared_length: Value reported via ``resp.content_length``.
        actual_body: Bytes actually streamed via ``iter_chunked`` — shorter
            than ``declared_length`` to simulate a truncated connection.

    Returns:
        MagicMock quacking like an aiohttp.ClientSession.
    """
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.status = 200
    mock_response.content_length = declared_length

    def _iter_chunked(chunk_size: int) -> AsyncIterator[bytes]:
        async def _gen() -> AsyncIterator[bytes]:
            yield actual_body

        return _gen()

    mock_response.content = MagicMock()
    mock_response.content.iter_chunked = _iter_chunked

    mock_session = MagicMock()
    mock_session.get = MagicMock(
        return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response),
            __aexit__=AsyncMock(return_value=False),
        )
    )
    return mock_session


@pytest.mark.asyncio
async def test_download_raises_on_truncated_body() -> None:
    """A body shorter than Content-Length must raise, not return silently."""
    session = _make_truncated_session(declared_length=100, actual_body=b"short")

    with pytest.raises(StaticGtfsLoadError, match="truncated|incomplete"):
        await download_zip_to_tempfile(
            _DUMMY_URL, session, max_download_bytes=1024 * 1024
        )
