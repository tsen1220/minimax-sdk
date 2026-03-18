"""Type definitions for the Video resource."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class VideoCreateResult(BaseModel):
    """Result of creating a video generation task."""

    task_id: str


class VideoQueryResult(BaseModel):
    """Result of querying a video generation task status."""

    task_id: str
    status: str
    file_id: Optional[str] = None
    video_width: Optional[int] = None
    video_height: Optional[int] = None


class VideoResult(BaseModel):
    """Final result of a completed video generation (extends TaskResult pattern).

    Returned by high-level methods that auto-poll until completion.
    """

    task_id: str
    status: str
    file_id: str
    download_url: Optional[str] = None
    video_width: int
    video_height: int
