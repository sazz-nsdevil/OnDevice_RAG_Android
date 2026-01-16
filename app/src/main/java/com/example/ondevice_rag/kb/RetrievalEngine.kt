package com.example.ondevice_rag.kb

import com.example.ondevice_rag.llama.LlamaManager

class RetrievalEngine(
    private val llamaManager: LlamaManager,
    private val packageManager: KbPackageManager
) {
    suspend fun retrieve(scopeId: String, query: String, k: Int): List<ChunkEntry> {
        val manifest = KbManifest.load(packageManager.manifestFile(scopeId))
        val embeddings = EmbeddingIndex.load(
            packageManager.embeddingsFile(scopeId),
            manifest.embeddingDim,
            manifest.chunkCount
        )
        val chunks = ChunkStore(packageManager.chunksFile(scopeId)).loadAll()
        val queryEmbedding = llamaManager.embed(query)
        val top = embeddings.topK(queryEmbedding, k)
        return top.mapNotNull { scored -> chunks.getOrNull(scored.index) }
    }
}
