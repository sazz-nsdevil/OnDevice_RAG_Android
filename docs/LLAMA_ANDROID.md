# llama.cpp Android Integration Plan

## Build (NDK + CMake)
1. Add llama.cpp as a Git submodule under `app/src/main/cpp/llama`.
2. Create `CMakeLists.txt` in `app/src/main/cpp/` that:
   - builds llama.cpp as a static library
   - builds a JNI shared library (e.g., `llama_jni`) that wraps model load/infer APIs
3. In `app/build.gradle.kts`:
   - enable `externalNativeBuild` with CMake
   - set `ndkVersion` and ABI filters (e.g., `arm64-v8a` only for performance)

## JNI interface design
Expose a minimal API for performance and simplicity:
```kotlin
external fun loadModel(path: String, contextSize: Int, threads: Int): Long
external fun freeModel(handle: Long)
external fun embed(handle: Long, text: String): FloatArray
external fun generate(
    handle: Long,
    prompt: String,
    maxTokens: Int,
    temperature: Float,
    topP: Float,
    callback: TokenCallback
)
```
- Each `handle` is a native pointer to a model/context instance.
- Instantiate **two** contexts on device:
  - LLM: `LiquidAI/LFM2.5-1.2B-Instruct-GGUF`
  - Embedding: `exp-models/dragonkue-KoEn-E5-Tiny` (GGUF)

## Threading / performance
- Use 2–4 threads on mid-range devices; expose configurable threads in `LlamaManager`.
- Keep embedding context size small (e.g., 512) to reduce memory.
- Stream tokens to UI via callback for low latency.

## JNI callback flow
- `generate()` pushes token strings via `TokenCallback.onToken()`.
- Kotlin `callbackFlow` is used to collect tokens into the UI.
