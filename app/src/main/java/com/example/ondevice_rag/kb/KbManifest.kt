package com.example.ondevice_rag.kb

import org.json.JSONObject
import java.io.File

class KbManifest(
    val version: String,
    val embeddingDim: Int,
    val chunkCount: Int
) {
    companion object {
        fun load(file: File): KbManifest {
            val json = JSONObject(file.readText())
            return KbManifest(
                version = json.getString("version"),
                embeddingDim = json.getInt("embedding_dim"),
                chunkCount = json.getInt("chunk_count")
            )
        }
    }
}
