"""Type definitions for the Files resource."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class FileInfo(BaseModel):
    """Information about an uploaded file."""

    file_id: str
    bytes: int
    created_at: int
    filename: str
    purpose: str
    download_url: Optional[str] = None


class FileList(BaseModel):
    """Result of listing files."""

    files: list[FileInfo] = []
