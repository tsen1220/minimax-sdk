# MiniMax SDK

Unofficial SDKs for MiniMax's multimodal APIs.

## Supported APIs

| API | Capabilities |
|-----|-------------|
| Text | Chat completion, streaming, tool use, extended thinking (via Anthropic-compatible endpoint) |
| Speech | TTS (sync, streaming, WebSocket, async long-text) |
| Voice | Clone, design, list, delete |
| Video | Text-to-video, image-to-video, first/last-frame, subject reference |
| Image | Text-to-image, image-to-image |
| Music | Generate, stream, lyrics |
| Files | Upload, list, retrieve, download, delete |

## Language SDKs

| Language | Status | Path |
|----------|--------|------|
| Python | Available | [`python/`](python/) |
| TypeScript | Coming soon | -- |

## Quick Start (Python)

```bash
pip install minimax-sdk
```

```python
from minimax_sdk import MiniMax

client = MiniMax(api_key="your-api-key")

# Text generation
result = client.text.create(
    model="MiniMax-M2.7",
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=1024,
)

# Text-to-Speech
audio = client.speech.tts(text="Hello world", model="speech-2.8-hd")
audio.save("hello.mp3")
```

See [python/README.md](python/README.md) for full documentation, configuration, and API reference.

## License

[MIT](LICENSE)
