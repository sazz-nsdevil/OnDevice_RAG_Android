package com.example.ondevice_rag.llama

object LlamaBridge {
    init {
        // System.loadLibrary("llama_jni")
    }

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
}

fun interface TokenCallback {
    fun onToken(token: String)
}
