# SDK Design Spec Review

> Reviewer: Deep Logic Reviewer (Claude Opus 4.6)
> Date: 2026-03-18
> Spec: `2026-03-18-sdk-design.md`

## Summary

The design spec is well-structured and covers the core MiniMax multimodal APIs with a clean resource-oriented pattern. The 26 endpoints are mapped to 6 resource mounts with sensible method names and a consistent auto-polling strategy. However, the review identified 18 issues ranging from endpoint coverage gaps to type definition inconsistencies and underspecified behaviors. The most impactful issues are around the endpoint count not actually adding up to 26, overlapping upload endpoints between Voice and Files, missing async counterparts for streaming methods, and several return type definitions that are incomplete or inconsistent with the API structure.

---

## Findings

### HIGH-1: Endpoint count does not add up to 26

**Location:** Section 3, title "26 total"

**Description:** Counting every distinct method listed in the tables yields:
- Speech: 5 (tts, tts_stream, connect, async_create, async_generate)
- Voice: 5 (upload_audio, clone, design, list, delete)
- Video: 7 (text_to_video, image_to_video, frames_to_video, subject_to_video, create, query, download)
- Image: 1 (generate, used two ways but it is one method)
- Music: 3 (generate, generate_stream, generate_lyrics)
- Files: 5 (upload, list, retrieve, retrieve_content, delete)

**Total: 26** -- but this counts both the high-level convenience wrappers (e.g., `text_to_video` which calls create+poll+download) and the low-level methods they compose (create, query, download). If the intent is 26 *API endpoints* (distinct HTTP/WS calls to MiniMax), the number is lower because:
- `text_to_video`, `image_to_video`, `frames_to_video`, `subject_to_video` all call the same `POST /v1/video_generation` endpoint.
- `async_generate` calls `async_create` + poll, not a separate endpoint.
- `voice.upload_audio` and `files.upload` both hit `POST /v1/files/upload`.
- `video.download` and `files.retrieve` both hit `GET /v1/files/retrieve`.

The actual distinct API endpoints are approximately 16-17. This matters because the "26 endpoints" claim will confuse implementors about whether they are tracking API surface area or SDK method count.

**Suggested fix:** Clarify the section title: "26 SDK methods mapping to N API endpoints." Add a mapping table from SDK method to underlying HTTP endpoint to make this unambiguous.

---

### HIGH-2: `voice.upload_audio` duplicates `files.upload` with no clear contract boundary

**Location:** Section 3, Voice table vs. Files table

**Description:** `voice.upload_audio(file, purpose)` calls `POST /v1/files/upload` and `files.upload(file, purpose)` also calls `POST /v1/files/upload`. The spec does not explain:
1. Why the duplication exists (convenience? different default `purpose`?).
2. Whether `voice.upload_audio` delegates to `files.upload` internally or reimplements the HTTP call.
3. What `purpose` values are valid for each (voice clone uses `"voice_clone"`, prompt audio uses `"voice_audio_detection"`).

This will cause implementor confusion and potential inconsistency in how uploads are handled.

**Suggested fix:** Either (a) have `voice.upload_audio` explicitly delegate to `self._client.files.upload(file, purpose)` and document the convenience purpose, or (b) remove `voice.upload_audio` and document in the Voice guide that users should call `client.files.upload(file, purpose="voice_clone")` first. Option (a) is better UX.

---

### HIGH-3: `video.download` duplicates `files.retrieve` -- same underlying endpoint

**Location:** Section 3, Video table vs. Files table

**Description:** `video.download(file_id)` maps to `GET /v1/files/retrieve`, which is the same endpoint as `files.retrieve(file_id)`. The spec does not clarify whether `video.download` returns a `FileInfo` (like `files.retrieve`) or does something additional (e.g., actually downloads the binary content). The name "download" implies it fetches the file bytes, but the endpoint only returns metadata + a download URL.

**Suggested fix:** Clarify the return type and behavior of `video.download`. If it just returns a URL, rename it to `video.get_download_url` or have it delegate to `files.retrieve`. If it actually downloads the binary, document that it calls `files.retrieve` then `files.retrieve_content`, and specify the return type.

---

### HIGH-4: Missing `async_query` and `async_retrieve` for Speech async tasks

**Location:** Section 3, Speech table

**Description:** Speech has `async_create` and `async_generate` (which auto-polls). But there is no low-level `async_query(task_id)` method to check the status of a long-text TTS task, nor an `async_retrieve(file_id)` to get the result. Video exposes both high-level (text_to_video) and low-level (create, query, download) methods, but Speech only exposes the high-level `async_generate` and the bare `async_create` with no way to query status.

If a user calls `async_create` (low-level), they have no SDK method to poll the result themselves.

**Suggested fix:** Add `speech.async_query(task_id)` mapping to `GET /v1/query/t2a_async_v2` (or the correct status endpoint) so users who call `async_create` can poll manually. This maintains the same high-level/low-level split used in Video.

---

### HIGH-5: `VideoResult` assumes single file_id but video generation can produce multiple files

**Location:** Section 4, `VideoResult`

**Description:** `VideoResult` has `file_id: str` (singular) and `download_url: str` (singular). However, the MiniMax video generation API response includes a `file_id` field in the query response that could vary per API version. More importantly, some video generation modes may return additional metadata (e.g., cover images). The singular `file_id` also does not account for potential batch generation in future API versions.

**Suggested fix:** Verify against the actual API response schema. If the query response nests `file_id` inside a result object, the mapping should be documented. Consider whether `VideoResult` should include the raw response for forward-compatibility.

---

### MEDIUM-1: `ImageResult` has no task/async model but image generation may be slow

**Location:** Section 3 and Section 4

**Description:** Image generation is listed as a direct `POST /v1/image_generation` with an `ImageResult` return. Unlike video, there is no polling flow. This is correct if the MiniMax image API is synchronous. However, if image generation is also async (task-based), the spec is missing the polling loop. The spec should explicitly confirm this is a synchronous API call.

**Suggested fix:** Add a note confirming image generation is synchronous (blocking HTTP call that returns directly) to distinguish it from the async video/speech patterns.

---

### MEDIUM-2: `AudioResponse.duration` type may be wrong

**Location:** Section 4, `AudioResponse`

**Description:** `duration: int` is documented as "Milliseconds." The MiniMax T2A API returns `duration_ms` as an integer in some cases but as a float in others (particularly for streaming where partial durations are reported). Using `int` will silently truncate fractional milliseconds. More importantly, some API responses return duration in seconds (not milliseconds) -- the spec should verify which unit the raw API uses and document the conversion.

**Suggested fix:** Verify the actual API response field name and unit. If the API returns seconds as a float, convert to milliseconds in the SDK and use `float` for `duration` to avoid truncation. Document the unit in the type definition.

---

### MEDIUM-3: `FileInfo.file_id` is typed as `int` but used as `str` everywhere else

**Location:** Section 4, `FileInfo` vs. all method signatures

**Description:** `FileInfo.file_id: int` but every method that accepts a file_id (e.g., `voice.clone(file_id, ...)`, `video.download(file_id)`, `files.retrieve(file_id)`) uses it as an opaque identifier. If the API returns file_id as an integer, passing it to other methods that construct URL paths will require `str()` conversion. If the API returns it as a string, the type should be `str`. The inconsistency between `FileInfo.file_id: int` and `TaskResult.file_id: str` is a bug.

**Suggested fix:** Unify `file_id` to a single type across all models. Check the API response -- MiniMax file IDs appear to be numeric but are typically handled as strings in API calls. Use `str` consistently or `int` consistently, but not both.

---

### MEDIUM-4: `VoiceCloneResult` is missing `voice_id`

**Location:** Section 4, `VoiceCloneResult`

**Description:** After cloning a voice, the user needs the `voice_id` to use it in TTS calls. `VoiceCloneResult` only contains `demo_audio` and `input_sensitive`, but not the `voice_id` of the newly cloned voice. The MiniMax voice clone API response does not return a voice_id directly (the user provides it as input), but the spec's `VoiceCloneResult` should at minimum echo back the `voice_id` for confirmation and downstream use.

**Suggested fix:** Add `voice_id: str` to `VoiceCloneResult` to echo the created voice ID. This is essential for chaining: `result = client.voice.clone(...); client.speech.tts(voice_id=result.voice_id, ...)`.

---

### MEDIUM-5: Missing return type for `voice.delete` and `voice.list` edge cases

**Location:** Section 3 and Section 4

**Description:** `voice.delete(voice_id, voice_type)` has no documented return type. Should it return `None` on success (with exceptions on failure), or a confirmation object? Similarly, `VoiceList` assumes all three categories (system_voice, voice_cloning, voice_generation) are always present in the response, but the API filters by `voice_type` parameter -- if a user requests only cloned voices, do the other lists come back empty or absent?

**Suggested fix:** Document return types for all methods: `voice.delete -> None`, `voice.list -> VoiceList`. Clarify whether `VoiceList` fields are always present or conditionally populated based on the `voice_type` filter.

---

### MEDIUM-6: `speech.tts_stream` return type is underspecified

**Location:** Section 3, Speech table

**Description:** `tts_stream` returns "iterator" but the spec does not specify `Iterator[bytes]`, `Iterator[AudioChunk]`, or `Iterator[AudioResponse]`. For streaming TTS, the MiniMax API sends hex-encoded audio chunks. The spec says hex is auto-decoded (Section 4 Principles), but does not define:
1. The exact yield type (raw bytes per chunk? an AudioChunk with metadata?).
2. Whether the iterator is a generator, an `httpx.Response` stream, or a custom class.
3. How end-of-stream is signaled.

**Suggested fix:** Define a `StreamChunk` type or specify that `tts_stream` yields `bytes` (decoded from hex). Also specify whether the total `AudioResponse` metadata (duration, sample_rate) is available after iteration completes (e.g., via a finalizer or summary attribute on the iterator).

---

### MEDIUM-7: `music.generate_stream` return type is underspecified

**Location:** Section 3, Music table

**Description:** Same issue as HIGH-6 above. `generate_stream` says "Streaming music" but does not specify the return type. Music streaming likely returns chunks of audio data, but the yield type, chunk format, and metadata availability are unspecified.

**Suggested fix:** Specify the return type consistently with `speech.tts_stream`. If both use the same streaming pattern, define a shared `AudioStream` type.

---

### MEDIUM-8: Retry includes error code 1002 (Rate Limit) which needs special backoff

**Location:** Section 6, Auto Retry

**Description:** Retryable codes include `1002` (Rate Limit). The retry strategy is "Exponential backoff (1s -> 2s -> 4s -> ...)". However, rate limit errors often come with a `Retry-After` header or similar hint from the API. Blindly retrying with generic exponential backoff may:
1. Not respect the server's requested wait time.
2. Cause the client to retry too aggressively if the rate limit window is long.

**Suggested fix:** For `1002`, check if the API response includes a `Retry-After` header or equivalent field and honor it. Fall back to exponential backoff only if no hint is provided. Document this behavior.

---

### MEDIUM-9: No specification of how `SpeechConnection` handles reconnection or errors mid-stream

**Location:** Section 7, WebSocket T2A

**Description:** The WebSocket connection has a 120-second idle timeout. The spec does not address:
1. What happens if the connection drops mid-`send()` (network error, server restart).
2. Whether auto-reconnect is attempted.
3. How errors during `send_stream()` are surfaced (exception mid-iteration? partial data?).
4. Whether `session_id` changes on reconnect.

**Suggested fix:** Document the error behavior: (a) connection drops raise `ConnectionError` (or a custom exception), (b) no auto-reconnect (user must create a new connection), (c) partial data from `send_stream()` is yielded up to the point of failure, then the exception is raised. Alternatively, if auto-reconnect is desired, specify the strategy.

---

### MEDIUM-10: `image.generate` overloading on `subject_reference` parameter is implicit

**Location:** Section 3, Image table

**Description:** The spec shows `image.generate` listed twice -- once without `subject_reference` (T2I) and once with it (I2I). This is the same Python method with optional parameters, but it hits the same endpoint with different behavior. The spec does not clarify:
1. Whether `subject_reference` is an optional parameter or triggers a different code path.
2. What type `subject_reference` is (file_id? URL? base64 image?).
3. Whether other parameters differ between T2I and I2I modes.

**Suggested fix:** Document `subject_reference` as an optional parameter with its type. Clarify that T2I vs. I2I is determined by presence/absence of this parameter. Specify the type (likely `list[str]` of file_ids based on the MiniMax API).

---

### LOW-1: No `__repr__` or `__str__` convention specified for response types

**Location:** Section 4

**Description:** Response types like `AudioResponse`, `VideoResult`, etc. are defined as data classes but the spec does not mention whether they should have useful string representations for debugging. An `AudioResponse` with `data: bytes` will print a massive byte string if `repr()` is called.

**Suggested fix:** Note in implementation guidelines that `AudioResponse.__repr__` should truncate or omit the `data` field. Pydantic models handle this reasonably by default, but if using dataclasses, this needs explicit handling.

---

### LOW-2: No versioning strategy for the SDK

**Location:** Entire spec

**Description:** The spec does not mention SDK versioning (semver?), how breaking API changes from MiniMax will be handled, or whether the SDK pins to a specific API version. The `base_url` defaults to `https://api.minimax.io` with no API version prefix, but endpoints use `/v1/` paths.

**Suggested fix:** Add a brief versioning section: SDK follows semver, API version is embedded in endpoint paths (`/v1/`), and the SDK will support one API version at a time.

---

### LOW-3: `.env` loading behavior not fully specified

**Location:** Section 2, Configuration

**Description:** The spec says ".env via python-dotenv" but does not specify:
1. Where the `.env` file is searched for (CWD? project root? traversing up?).
2. Whether `.env` loading is opt-in or automatic on `MiniMax()` construction.
3. Whether an explicit `dotenv_path` parameter is available.

Auto-loading `.env` in a library (as opposed to an application) is controversial -- it can cause surprising behavior when the SDK is used as a dependency.

**Suggested fix:** Make `.env` loading explicit: `MiniMax(dotenv=True)` or `MiniMax(dotenv_path=".env")` with a default of `False`. Alternatively, document that it uses `find_dotenv()` from python-dotenv and only loads if a `.env` file exists in the current working directory.

---

## Positive Observations

1. **Clean resource-oriented design.** The `client.resource.method()` pattern is intuitive and mirrors modern SDK conventions (Stripe, OpenAI).

2. **Auto-polling is the right default.** Having high-level methods that handle the create-poll-download loop while also exposing low-level primitives is excellent API design.

3. **Hex auto-decode is a good decision.** Users should never have to deal with hex-encoded audio. Abstracting this into `AudioResponse` with `save()` and `to_base64()` helpers is user-friendly.

4. **Exception hierarchy is well-thought-out.** Mapping MiniMax error codes to semantic exception types lets users write targeted error handling (`except ContentSafetyError`) without memorizing numeric codes.

5. **Both sync and async clients.** Supporting `MiniMax` and `AsyncMiniMax` from day one avoids a painful retrofit later.

6. **Method-level poll configuration.** Allowing `poll_interval` and `poll_timeout` overrides per call is more flexible than only global configuration.

---

## Remaining Questions

1. **T2A async query endpoint:** What is the actual HTTP endpoint for querying long-text TTS task status? The spec shows `async_create` maps to `POST /v1/t2a_async_v2` but never shows the corresponding query endpoint. Is it `GET /v1/query/t2a_async_v2`?

2. **Music generation -- sync or async?** Is music generation synchronous (like image) or task-based (like video)? The spec shows a direct return of `AudioResponse` suggesting sync, but music generation can take significant time.

3. **Voice list API uses POST not GET.** The spec shows `POST /v1/get_voice` for listing voices. Is this correct? Using POST for a read operation is unusual -- it may indicate the API requires a request body with filters.

4. **WebSocket authentication.** How is the API key passed in the WebSocket connection? As a query parameter in the WSS URL? As a header during the upgrade handshake? This affects the `connect()` implementation.

5. **File purpose values.** What are the valid `purpose` values for `files.upload`? The spec does not enumerate them. Known ones from context: `"voice_clone"`, `"voice_audio_detection"`, but there may be others for video reference images, etc.

6. **Image generation response format.** Does the API always return both `image_urls` and `image_base64`, or is it one or the other based on a request parameter? The `ImageResult` type includes both but they may be mutually exclusive.
