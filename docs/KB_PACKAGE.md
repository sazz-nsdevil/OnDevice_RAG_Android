# KB Package Layout

## ZIP layout
```
kb_<scopeId>_<version>.zip
├─ manifest.json
├─ embeddings.f16
└─ chunks.jsonl
```

## manifest.json schema (minimal)
```json
{
  "version": "v1",
  "embedding_dim": 384,
  "chunk_count": 1234,
  "sha256": {
    "embeddings.f16": "<hex>",
    "chunks.jsonl": "<hex>",
    "manifest.json": "<hex>"
  }
}
```

## embeddings.f16
- Raw float16 vectors (little-endian), flattened as:
  `[chunk0_dim0, chunk0_dim1, ... chunk0_dimN, chunk1_dim0, ...]`.

## chunks.jsonl
- JSONL file with one chunk per line:
```json
{"id":"chunk-0001","text":"...","source":"doc.pdf#p3"}
```

## Notes
- The server should provide a SHA-256 of the ZIP for end-to-end download verification.
- Embedding dimensions must match the on-device embedding model.
