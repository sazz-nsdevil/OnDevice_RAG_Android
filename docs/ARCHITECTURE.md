# Offline-first RAG Architecture (Android)

## Minimal project structure
```
OnDevice_RAG_Android/
├─ app/
│  ├─ src/main/java/com/example/ondevice_rag/
│  │  ├─ data/              # Auth + basic models
│  │  ├─ kb/                # KB storage, retrieval, download
│  │  ├─ llama/             # JNI bridge + manager
│  │  ├─ ui/                # ViewModel + state
│  │  ├─ ui/screens/        # Compose screens
│  │  ├─ ui/theme/          # Compose theme
│  │  ├─ util/              # zip + checksum
│  │  └─ worker/            # WorkManager tasks
│  └─ src/main/res/
└─ docs/
   ├─ ARCHITECTURE.md
   ├─ KB_PACKAGE.md
   └─ LLAMA_ANDROID.md
```

## Screen flow
1. **Login** → call Auth/Entitlements service (stubbed in `AuthRepository`).
2. **Grade/Subject selection** → choose scope and trigger KB download.
3. **Chat** → local retrieval + on-device LLM generation, streaming tokens.

## Offline-first data flow
1. User selects a scope.
2. WorkManager downloads KB ZIP via OkHttp.
3. Worker verifies SHA-256 checksum and unzips into `filesDir/kb/<scopeId>/`.
4. `KbMetadataStore` stores installed version.
5. Chat retrieval loads embeddings + chunks from internal storage and runs cosine search.
6. Prompt is assembled and sent to llama.cpp LLM.
