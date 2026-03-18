"""Tests for minimax_sdk._base — SyncResource, AsyncResource, _decode_audio."""

from __future__ import annotations

from unittest.mock import MagicMock

from minimax_sdk._base import AsyncResource, SyncResource, _decode_audio
from minimax_sdk._http import AsyncHttpClient, HttpClient


class TestSyncResource:
    def test_stores_http_and_client(self) -> None:
        mock_http = MagicMock(spec=HttpClient)
        mock_client = MagicMock()  # simulates MiniMax

        resource = SyncResource(mock_http, client=mock_client)

        assert resource._http is mock_http
        assert resource._client is mock_client

    def test_client_defaults_to_none(self) -> None:
        mock_http = MagicMock(spec=HttpClient)

        resource = SyncResource(mock_http)

        assert resource._http is mock_http
        assert resource._client is None


class TestAsyncResource:
    def test_stores_http_and_client(self) -> None:
        mock_http = MagicMock(spec=AsyncHttpClient)
        mock_client = MagicMock()  # simulates AsyncMiniMax

        resource = AsyncResource(mock_http, client=mock_client)

        assert resource._http is mock_http
        assert resource._client is mock_client

    def test_client_defaults_to_none(self) -> None:
        mock_http = MagicMock(spec=AsyncHttpClient)

        resource = AsyncResource(mock_http)

        assert resource._http is mock_http
        assert resource._client is None


class TestDecodeAudio:
    def test_decodes_hex_string(self) -> None:
        hex_str = "48656c6c6f"  # "Hello" in hex
        result = _decode_audio(hex_str)
        assert result == b"Hello"

    def test_empty_string(self) -> None:
        assert _decode_audio("") == b""

    def test_binary_data_roundtrip(self) -> None:
        original = b"\x00\x01\x02\xff"
        hex_str = original.hex()
        assert _decode_audio(hex_str) == original
