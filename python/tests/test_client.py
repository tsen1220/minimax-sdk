"""Tests for minimax_sdk.client."""

from __future__ import annotations

import os

import pytest

from minimax_sdk.client import MiniMax
from minimax_sdk.resources.files import Files
from minimax_sdk.resources.image import Image
from minimax_sdk.resources.music import Music
from minimax_sdk.resources.speech import Speech
from minimax_sdk.resources.video import Video
from minimax_sdk.resources.voice import Voice


# ── Initialisation ───────────────────────────────────────────────────────────


class TestClientInitialisation:
    def test_missing_api_key_raises_value_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
        with pytest.raises(ValueError, match="API key is required"):
            MiniMax(load_dotenv=False)

    def test_empty_string_api_key_raises_value_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
        with pytest.raises(ValueError, match="API key is required"):
            MiniMax(api_key="", load_dotenv=False)

    def test_client_with_api_key_creates_resources(
        self, minimax_client: MiniMax
    ) -> None:
        assert hasattr(minimax_client, "speech")
        assert hasattr(minimax_client, "voice")
        assert hasattr(minimax_client, "video")
        assert hasattr(minimax_client, "image")
        assert hasattr(minimax_client, "music")
        assert hasattr(minimax_client, "files")


# ── Resource types ───────────────────────────────────────────────────────────


class TestResourceTypes:
    def test_speech_resource_type(self, minimax_client: MiniMax) -> None:
        assert isinstance(minimax_client.speech, Speech)

    def test_voice_resource_type(self, minimax_client: MiniMax) -> None:
        assert isinstance(minimax_client.voice, Voice)

    def test_video_resource_type(self, minimax_client: MiniMax) -> None:
        assert isinstance(minimax_client.video, Video)

    def test_image_resource_type(self, minimax_client: MiniMax) -> None:
        assert isinstance(minimax_client.image, Image)

    def test_music_resource_type(self, minimax_client: MiniMax) -> None:
        assert isinstance(minimax_client.music, Music)

    def test_files_resource_type(self, minimax_client: MiniMax) -> None:
        assert isinstance(minimax_client.files, Files)


# ── Configuration resolution ─────────────────────────────────────────────────


class TestConfigResolution:
    def test_param_takes_priority_over_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("MINIMAX_BASE_URL", "https://env.example.com")
        client = MiniMax(
            api_key="sk-test",
            base_url="https://param.example.com",
            load_dotenv=False,
        )
        assert client._http_client.base_url == "https://param.example.com"

    def test_env_var_takes_priority_over_default(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("MINIMAX_API_KEY", "sk-from-env")
        monkeypatch.setenv("MINIMAX_BASE_URL", "https://env.example.com")
        client = MiniMax(load_dotenv=False)
        assert client._http_client.base_url == "https://env.example.com"

    def test_default_base_url_when_nothing_set(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("MINIMAX_BASE_URL", raising=False)
        client = MiniMax(api_key="sk-test", load_dotenv=False)
        assert client._http_client.base_url == "https://api.minimax.io"

    def test_poll_interval_from_param(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("MINIMAX_POLL_INTERVAL", raising=False)
        client = MiniMax(
            api_key="sk-test", poll_interval=10.0, load_dotenv=False
        )
        assert client.poll_interval == 10.0

    def test_poll_timeout_from_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("MINIMAX_POLL_TIMEOUT", "1200")
        client = MiniMax(api_key="sk-test", load_dotenv=False)
        assert client.poll_timeout == 1200.0

    def test_max_retries_from_param(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("MINIMAX_MAX_RETRIES", raising=False)
        client = MiniMax(
            api_key="sk-test", max_retries=5, load_dotenv=False
        )
        assert client._http_client.max_retries == 5

    def test_api_key_from_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("MINIMAX_API_KEY", "sk-env-key")
        client = MiniMax(load_dotenv=False)
        assert client._http_client.api_key == "sk-env-key"


# ── load_dotenv=False ────────────────────────────────────────────────────────


class TestLoadDotenv:
    def test_load_dotenv_false_skips_env_loading(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path
    ) -> None:
        """Ensure that load_dotenv=False does not read a .env file."""
        # Create a .env file that would set MINIMAX_BASE_URL
        env_file = tmp_path / ".env"
        env_file.write_text("MINIMAX_BASE_URL=https://dotenv.example.com\n")

        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("MINIMAX_BASE_URL", raising=False)

        client = MiniMax(api_key="sk-test", load_dotenv=False)
        # Should use the default, not the .env value
        assert client._http_client.base_url == "https://api.minimax.io"


# ── Context manager ──────────────────────────────────────────────────────────


class TestContextManager:
    def test_context_manager(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
        with MiniMax(api_key="sk-test", load_dotenv=False) as client:
            assert isinstance(client, MiniMax)


# ── __repr__ ────────────────────────────────────────────────────────────────


class TestMiniMaxRepr:
    def test_repr_contains_base_url_and_poll_settings(
        self, minimax_client: MiniMax
    ) -> None:
        r = repr(minimax_client)
        assert "MiniMax(" in r
        assert "base_url=" in r
        assert "poll_interval=" in r
        assert "poll_timeout=" in r


# ── load_dotenv=True (default) ──────────────────────────────────────────────


class TestLoadDotenvTrue:
    def test_load_dotenv_true_calls_dotenv(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path
    ) -> None:
        """Ensure load_dotenv=True triggers dotenv.load_dotenv (line 144)."""
        from unittest.mock import patch

        env_file = tmp_path / ".env"
        env_file.write_text("MINIMAX_API_KEY=sk-from-dotenv\n")

        monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
        monkeypatch.delenv("MINIMAX_BASE_URL", raising=False)

        with patch("minimax_sdk.client.dotenv.find_dotenv", return_value=str(env_file)):
            client = MiniMax(load_dotenv=True)
        assert client._http_client.api_key == "sk-from-dotenv"


# ── AsyncMiniMax ────────────────────────────────────────────────────────────

from minimax_sdk.client import AsyncMiniMax
from minimax_sdk.resources.files import AsyncFiles
from minimax_sdk.resources.image import AsyncImage
from minimax_sdk.resources.music import AsyncMusic
from minimax_sdk.resources.speech import AsyncSpeech
from minimax_sdk.resources.video import AsyncVideo
from minimax_sdk.resources.voice import AsyncVoice


class TestAsyncMiniMaxInitialisation:
    def test_missing_api_key_raises_value_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
        with pytest.raises(ValueError, match="API key is required"):
            AsyncMiniMax(load_dotenv=False)

    def test_async_client_creates_all_resources(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
        client = AsyncMiniMax(api_key="sk-test-async", load_dotenv=False)
        assert isinstance(client.speech, AsyncSpeech)
        assert isinstance(client.voice, AsyncVoice)
        assert isinstance(client.video, AsyncVideo)
        assert isinstance(client.image, AsyncImage)
        assert isinstance(client.music, AsyncMusic)
        assert isinstance(client.files, AsyncFiles)

    def test_async_client_load_dotenv_true(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path
    ) -> None:
        """Ensure AsyncMiniMax with load_dotenv=True loads .env file."""
        from unittest.mock import patch

        env_file = tmp_path / ".env"
        env_file.write_text("MINIMAX_API_KEY=sk-async-dotenv\n")
        monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
        monkeypatch.delenv("MINIMAX_BASE_URL", raising=False)

        with patch("minimax_sdk.client.dotenv.find_dotenv", return_value=str(env_file)):
            client = AsyncMiniMax(load_dotenv=True)
        assert client._http_client.api_key == "sk-async-dotenv"


class TestAsyncMiniMaxConfigResolution:
    def test_param_takes_priority_over_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("MINIMAX_BASE_URL", "https://env.example.com")
        client = AsyncMiniMax(
            api_key="sk-test",
            base_url="https://param.example.com",
            load_dotenv=False,
        )
        assert client._http_client.base_url == "https://param.example.com"

    def test_env_var_takes_priority_over_default(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("MINIMAX_API_KEY", "sk-from-env")
        monkeypatch.setenv("MINIMAX_BASE_URL", "https://env.example.com")
        client = AsyncMiniMax(load_dotenv=False)
        assert client._http_client.base_url == "https://env.example.com"

    def test_default_base_url_when_nothing_set(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("MINIMAX_BASE_URL", raising=False)
        client = AsyncMiniMax(api_key="sk-test", load_dotenv=False)
        assert client._http_client.base_url == "https://api.minimax.io"

    def test_poll_interval_from_param(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("MINIMAX_POLL_INTERVAL", raising=False)
        client = AsyncMiniMax(
            api_key="sk-test", poll_interval=10.0, load_dotenv=False
        )
        assert client.poll_interval == 10.0

    def test_poll_timeout_from_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("MINIMAX_POLL_TIMEOUT", "1200")
        client = AsyncMiniMax(api_key="sk-test", load_dotenv=False)
        assert client.poll_timeout == 1200.0

    def test_max_retries_from_param(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("MINIMAX_MAX_RETRIES", raising=False)
        client = AsyncMiniMax(
            api_key="sk-test", max_retries=5, load_dotenv=False
        )
        assert client._http_client.max_retries == 5

    def test_timeout_params(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
        client = AsyncMiniMax(
            api_key="sk-test",
            timeout_connect=1.0,
            timeout_read=2.0,
            timeout_write=3.0,
            timeout_pool=4.0,
            load_dotenv=False,
        )
        assert client._http_client.api_key == "sk-test"


class TestAsyncMiniMaxContextManager:
    @pytest.mark.asyncio
    async def test_async_context_manager(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
        async with AsyncMiniMax(api_key="sk-test", load_dotenv=False) as client:
            assert isinstance(client, AsyncMiniMax)

    @pytest.mark.asyncio
    async def test_async_close(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
        client = AsyncMiniMax(api_key="sk-test", load_dotenv=False)
        await client.close()


class TestAsyncMiniMaxRepr:
    def test_repr_contains_base_url_and_poll_settings(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
        client = AsyncMiniMax(api_key="sk-test", load_dotenv=False)
        r = repr(client)
        assert "AsyncMiniMax(" in r
        assert "base_url=" in r
        assert "poll_interval=" in r
        assert "poll_timeout=" in r
