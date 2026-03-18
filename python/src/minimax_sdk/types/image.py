"""Type definitions for the Image resource."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ImageSubjectReference(BaseModel):
    """Subject reference for image-to-image generation."""

    type: str  # Currently only "character"
    image_file: str  # Public URL or base64 data URL


class ImageGenerationRequest(BaseModel):
    """Request body for image generation (POST /v1/image_generation)."""

    model: str
    prompt: str
    aspect_ratio: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    response_format: Optional[str] = None
    seed: Optional[int] = None
    n: Optional[int] = None
    prompt_optimizer: Optional[bool] = None
    subject_reference: Optional[list[ImageSubjectReference]] = None


class ImageResult(BaseModel):
    """Result of an image generation request."""

    id: str
    image_urls: Optional[list[str]] = None
    image_base64: Optional[list[str]] = None
    success_count: int = 0
    failed_count: int = 0
