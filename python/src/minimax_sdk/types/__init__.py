"""MiniMax SDK type definitions.

All types are Pydantic v2 BaseModel subclasses.
"""

from minimax_sdk.types.files import FileInfo, FileList
from minimax_sdk.types.image import (
    ImageGenerationRequest,
    ImageResult,
    ImageSubjectReference,
)
from minimax_sdk.types.music import (
    LyricsGenerationRequest,
    LyricsResult,
    MusicAudioSetting,
    MusicGenerationRequest,
)
from minimax_sdk.types.speech import (
    AudioSetting,
    T2AAsyncCreateRequest,
    T2AAsyncResult,
    T2ARequest,
    VoiceModify,
    VoiceSetting,
)
from minimax_sdk.types.video import (
    SubjectReference,
    VideoCreateResult,
    VideoGenerationRequest,
    VideoQueryResult,
    VideoResult,
)
from minimax_sdk.types.voice import (
    ClonePrompt,
    VoiceCloneRequest,
    VoiceCloneResult,
    VoiceDesignRequest,
    VoiceDesignResult,
    VoiceInfo,
    VoiceList,
)

__all__ = [
    # speech
    "AudioSetting",
    "T2AAsyncCreateRequest",
    "T2AAsyncResult",
    "T2ARequest",
    "VoiceModify",
    "VoiceSetting",
    # voice
    "ClonePrompt",
    "VoiceCloneRequest",
    "VoiceCloneResult",
    "VoiceDesignRequest",
    "VoiceDesignResult",
    "VoiceInfo",
    "VoiceList",
    # video
    "SubjectReference",
    "VideoCreateResult",
    "VideoGenerationRequest",
    "VideoQueryResult",
    "VideoResult",
    # image
    "ImageGenerationRequest",
    "ImageResult",
    "ImageSubjectReference",
    # music
    "LyricsGenerationRequest",
    "LyricsResult",
    "MusicAudioSetting",
    "MusicGenerationRequest",
    # files
    "FileInfo",
    "FileList",
]
