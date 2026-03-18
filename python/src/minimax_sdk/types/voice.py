"""Type definitions for the Voice resource."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel


class ClonePrompt(BaseModel):
    """Prompt audio reference for voice cloning."""

    prompt_audio: str
    prompt_text: str


class VoiceCloneRequest(BaseModel):
    """Request body for voice cloning (POST /v1/voice_clone)."""

    file_id: str
    voice_id: str
    clone_prompt: Optional[ClonePrompt] = None
    text: Optional[str] = None
    model: Optional[str] = None
    language_boost: Optional[str] = None
    need_noise_reduction: Optional[bool] = None
    need_volume_normalization: Optional[bool] = None


class VoiceCloneResult(BaseModel):
    """Result of a voice clone operation."""

    voice_id: str
    demo_audio: Optional[Any] = None  # AudioResponse when available
    input_sensitive: Optional[dict[str, Any]] = None


class VoiceDesignRequest(BaseModel):
    """Request body for voice design (POST /v1/voice_design)."""

    prompt: str
    preview_text: str
    voice_id: Optional[str] = None


class VoiceDesignResult(BaseModel):
    """Result of a voice design operation."""

    voice_id: str
    trial_audio: Any = None  # AudioResponse when available


class VoiceInfo(BaseModel):
    """Information about a single voice."""

    voice_id: str
    voice_name: Optional[str] = None
    description: list[str] = []
    created_time: Optional[str] = None


class VoiceList(BaseModel):
    """Result of listing voices."""

    system_voice: list[VoiceInfo] = []
    voice_cloning: list[VoiceInfo] = []
    voice_generation: list[VoiceInfo] = []
