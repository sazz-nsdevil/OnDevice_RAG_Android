package com.example.ondevice_rag.llama

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import kotlinx.coroutines.withContext

class LlamaManager {
    private var llmHandle: Long = 0
    private var embedHandle: Long = 0

    suspend fun loadModels(llmPath: String, embedPath: String, threads: Int) {
        withContext(Dispatchers.IO) {
            if (llmHandle != 0L) {
                LlamaBridge.freeModel(llmHandle)
            }
            if (embedHandle != 0L) {
                LlamaBridge.freeModel(embedHandle)
            }
            llmHandle = LlamaBridge.loadModel(llmPath, contextSize = 2048, threads = threads)
            embedHandle = LlamaBridge.loadModel(embedPath, contextSize = 512, threads = threads)
        }
    }

    suspend fun embed(text: String): FloatArray = withContext(Dispatchers.IO) {
        require(embedHandle != 0L) { "Embedding model not loaded" }
        LlamaBridge.embed(embedHandle, text)
    }

    fun generate(prompt: String, maxTokens: Int = 256): Flow<String> {
        require(llmHandle != 0L) { "LLM model not loaded" }
        return callbackFlow {
            val callback = TokenCallback { token ->
                trySend(token)
            }
            LlamaBridge.generate(
                handle = llmHandle,
                prompt = prompt,
                maxTokens = maxTokens,
                temperature = 0.7f,
                topP = 0.9f,
                callback = callback
            )
            close()
            awaitClose {}
        }
    }

    fun close() {
        if (llmHandle != 0L) {
            LlamaBridge.freeModel(llmHandle)
            llmHandle = 0L
        }
        if (embedHandle != 0L) {
            LlamaBridge.freeModel(embedHandle)
            embedHandle = 0L
        }
    }
}
