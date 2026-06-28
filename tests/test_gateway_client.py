import pytest
from unittest.mock import AsyncMock, patch
from shibaclaw.webui.gateway_client import _http_get, _http_post, _http_delete


class MockStreamReader:
    def __init__(self, response_bytes: bytes):
        self.response_bytes = response_bytes
        self.read_count = 0

    async def read(self, limit: int = -1):
        if self.read_count > 0:
            return b""
        self.read_count += 1
        return self.response_bytes


class MockStreamWriter:
    def __init__(self):
        self.written_data = b""
        self.is_closed = False

    def write(self, data: bytes):
        self.written_data += data

    async def drain(self):
        pass

    def close(self):
        self.is_closed = True

    async def wait_closed(self):
        pass


@pytest.mark.asyncio
async def test_http_get_success():
    resp = b"HTTP/1.1 200 OK\r\n\r\n{\"result\": \"success\"}"
    reader = MockStreamReader(resp)
    writer = MockStreamWriter()

    with patch("asyncio.open_connection", AsyncMock(return_value=(reader, writer))):
        res = await _http_get(["localhost"], 8000, "/api/test", "token123")
        assert res == {"result": "success"}
        assert b"GET /api/test HTTP/1.0" in writer.written_data
        assert b"Authorization: Bearer token123" in writer.written_data


@pytest.mark.asyncio
async def test_http_get_fail_status_body_200():
    resp = b"HTTP/1.1 500 Internal Server Error\r\n\r\n{\"code\": 200, \"msg\": \"fake 200\"}"
    reader = MockStreamReader(resp)
    writer = MockStreamWriter()

    with patch("asyncio.open_connection", AsyncMock(return_value=(reader, writer))):
        res = await _http_get(["localhost"], 8000, "/api/test", "token123")
        assert res is None


@pytest.mark.asyncio
async def test_http_post_success():
    resp = b"HTTP/1.1 200 OK\r\n\r\n{\"status\": \"created\"}"
    reader = MockStreamReader(resp)
    writer = MockStreamWriter()

    with patch("asyncio.open_connection", AsyncMock(return_value=(reader, writer))):
        res = await _http_post(["localhost"], 8000, "/api/test", {"data": "val"}, "token123")
        assert res == {"status": "created"}
        assert b"POST /api/test HTTP/1.0" in writer.written_data
        assert b"{\"data\": \"val\"}" in writer.written_data


@pytest.mark.asyncio
async def test_http_post_fail_status_body_200():
    resp = b"HTTP/1.1 400 Bad Request\r\n\r\n{\"err\": 200}"
    reader = MockStreamReader(resp)
    writer = MockStreamWriter()

    with patch("asyncio.open_connection", AsyncMock(return_value=(reader, writer))):
        res = await _http_post(["localhost"], 8000, "/api/test", {"data": "val"}, "token123")
        assert res is None


@pytest.mark.asyncio
async def test_http_delete_success():
    resp = b"HTTP/1.1 200 OK\r\n\r\n{\"deleted\": true}"
    reader = MockStreamReader(resp)
    writer = MockStreamWriter()

    with patch("asyncio.open_connection", AsyncMock(return_value=(reader, writer))):
        res = await _http_delete(["localhost"], 8000, "/api/test", "token123")
        assert res == {"deleted": True}
        assert b"DELETE /api/test HTTP/1.0" in writer.written_data


@pytest.mark.asyncio
async def test_http_delete_fail_status_body_200():
    resp = b"HTTP/1.1 403 Forbidden\r\n\r\n{\"reason\": \"no permission 200\"}"
    reader = MockStreamReader(resp)
    writer = MockStreamWriter()

    with patch("asyncio.open_connection", AsyncMock(return_value=(reader, writer))):
        res = await _http_delete(["localhost"], 8000, "/api/test", "token123")
        assert res is None
