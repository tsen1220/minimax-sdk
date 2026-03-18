# MiniMax SDK

Python SDK for [MiniMax](https://platform.minimax.io/) multimodal APIs — Speech, Voice, Video, Image, Music, and File management.

## Installation

```bash
pip install minimax-sdk
```

## Quick Start

```python
from minimax_sdk import MiniMax

client = MiniMax(api_key="your-api-key")

# Text-to-Speech
audio = client.speech.tts(text="Hello world", model="speech-2.8-hd")
audio.save("hello.mp3")

# Generate an image
result = client.image.generate(prompt="A cat on the moon", model="image-01")
print(result.image_urls)

# Generate a video (auto-polls until complete)
result = client.video.text_to_video(prompt="A sunrise over the ocean", model="MiniMax-Hailuo-2.3")
print(result.download_url)
```

## Configuration

Create a `.env` file or set environment variables:

```bash
MINIMAX_API_KEY=your-api-key
```

All settings are configurable:

```python
client = MiniMax(
    api_key="...",
    base_url="https://api.minimax.io",    # default
    max_retries=2,                         # auto-retry on server errors
    poll_interval=5.0,                     # async task polling interval (seconds)
    poll_timeout=600,                      # async task max wait time (seconds)
)
```

See [.env.example](.env.example) for all available options.

## Resources

### Speech — `client.speech`

```python
# Synchronous TTS
audio = client.speech.tts(
    text="Hello world",
    model="speech-2.8-hd",
    voice_setting={"voice_id": "English_expressive_narrator", "speed": 1.0},
    audio_setting={"format": "mp3", "sample_rate": 32000},
)
audio.save("output.mp3")

# Streaming TTS
for chunk in client.speech.tts_stream(text="Hello world", model="speech-2.8-hd"):
    player.write(chunk)

# WebSocket (real-time, multi-turn)
with client.speech.connect(
    model="speech-2.8-hd",
    voice_setting={"voice_id": "English_expressive_narrator"},
) as conn:
    audio = conn.send("Hello, how are you?")
    audio.save("chunk1.mp3")
    audio = conn.send("I'm doing great.")
    audio.save("chunk2.mp3")

# Long-text async (up to 100K characters)
result = client.speech.async_generate(
    text="Very long text...",
    model="speech-2.8-hd",
    voice_setting={"voice_id": "English_expressive_narrator"},
)
print(result.download_url)
```

### Voice — `client.voice`

```python
# Clone a voice
file_info = client.voice.upload_audio("reference.mp3")
result = client.voice.clone(file_id=file_info.file_id, voice_id="my-custom-voice")

# Design a voice from description
result = client.voice.design(
    prompt="A warm, friendly male narrator",
    preview_text="Hello, welcome to our show.",
)
result.trial_audio.save("preview.mp3")
print(result.voice_id)  # use this in TTS calls

# List & delete
voices = client.voice.list(voice_type="voice_cloning")
client.voice.delete(voice_id="my-custom-voice", voice_type="voice_cloning")
```

### Video — `client.video`

```python
# Text to video (auto-polls until complete)
result = client.video.text_to_video(
    prompt="A cat playing piano",
    model="MiniMax-Hailuo-2.3",
    duration=6,
    resolution="1080P",
)
print(result.download_url)

# Image to video
result = client.video.image_to_video(
    first_frame_image="https://example.com/photo.jpg",
    prompt="The scene comes alive",
    model="MiniMax-Hailuo-2.3",
)

# First & last frame
result = client.video.frames_to_video(
    last_frame_image="https://example.com/end.jpg",
    first_frame_image="https://example.com/start.jpg",
    model="MiniMax-Hailuo-02",
)

# Subject reference (face)
result = client.video.subject_to_video(
    subject_reference=[{"type": "character", "image": ["https://example.com/face.jpg"]}],
    prompt="A person waving at the camera",
    model="S2V-01",
)

# Low-level control
task = client.video.create(model="MiniMax-Hailuo-2.3", prompt="...")
status = client.video.query(task["task_id"])
```

### Image — `client.image`

```python
# Text to image
result = client.image.generate(
    prompt="A futuristic city at sunset",
    model="image-01",
    aspect_ratio="16:9",
    n=3,
)
print(result.image_urls)

# Image to image (with character reference)
result = client.image.generate(
    prompt="A woman in a garden",
    model="image-01",
    subject_reference=[{"type": "character", "image_file": "https://example.com/face.jpg"}],
)
```

### Music — `client.music`

```python
# Generate a song
audio = client.music.generate(
    model="music-2.5+",
    prompt="Indie folk, melancholic mood",
    lyrics="[Verse]\nWalking down the empty road\n[Chorus]\nBut I know the sun will rise",
)
audio.save("song.mp3")

# Generate lyrics first, then music
lyrics = client.music.generate_lyrics(
    mode="write_full_song",
    prompt="A cheerful summer love song",
)
print(lyrics.lyrics)

audio = client.music.generate(model="music-2.5+", lyrics=lyrics.lyrics)
audio.save("summer.mp3")

# Instrumental
audio = client.music.generate(
    model="music-2.5+",
    prompt="Lo-fi hip hop beats",
    is_instrumental=True,
)
```

### Files — `client.files`

```python
file_info = client.files.upload("audio.mp3", purpose="voice_clone")
files = client.files.list(purpose="voice_clone")
info = client.files.retrieve(file_id="123")
content = client.files.retrieve_content(file_id="123")
client.files.delete(file_id="123", purpose="voice_clone")
```

## Text Generation

Text generation uses the [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python) with MiniMax's compatible endpoint:

```python
import anthropic

client = anthropic.Anthropic(
    api_key="your-minimax-api-key",
    base_url="https://api.minimax.io/anthropic",
)

message = client.messages.create(
    model="MiniMax-M2.5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)
print(message.content[0].text)
```

## Async Support

Every resource has an async counterpart:

```python
from minimax_sdk import AsyncMiniMax

client = AsyncMiniMax(api_key="your-api-key")

audio = await client.speech.tts(text="Hello", model="speech-2.8-hd")
result = await client.video.text_to_video(prompt="...", model="MiniMax-Hailuo-2.3")
```

## Error Handling

```python
from minimax_sdk import MiniMax, RateLimitError, ContentSafetyError, AuthError, MiniMaxError

client = MiniMax(api_key="your-api-key")

try:
    result = client.video.text_to_video(prompt="...")
except RateLimitError:
    # Auto-retried, only raised after max_retries exceeded
    pass
except ContentSafetyError:
    # Input or output content violation
    pass
except AuthError:
    # Invalid API key
    pass
except MiniMaxError as e:
    # Catch-all for any MiniMax error
    print(f"Error {e.code}: {e.message}")
```

## License

[MIT](LICENSE)
