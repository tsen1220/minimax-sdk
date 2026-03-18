"""Type definitions for the Music resource."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class MusicAudioSetting(BaseModel):
    """Audio output configuration for music generation."""

    sample_rate: Optional[int] = None
    bitrate: Optional[int] = None
    format: Optional[str] = None


class MusicGenerationRequest(BaseModel):
    """Request body for music generation (POST /v1/music_generation)."""

    model: str
    prompt: Optional[str] = None
    lyrics: Optional[str] = None
    stream: Optional[bool] = False
    output_format: Optional[str] = None
    lyrics_optimizer: Optional[bool] = None
    is_instrumental: Optional[bool] = None
    audio_setting: Optional[MusicAudioSetting] = None


class LyricsGenerationRequest(BaseModel):
    """Request body for lyrics generation (POST /v1/lyrics_generation)."""

    mode: str
    prompt: Optional[str] = None
    lyrics: Optional[str] = None
    title: Optional[str] = None


class LyricsResult(BaseModel):
    """Result of a lyrics generation request."""

    song_title: str
    style_tags: str
    lyrics: str
