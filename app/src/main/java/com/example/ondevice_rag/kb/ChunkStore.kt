package com.example.ondevice_rag.kb

import org.json.JSONObject
import java.io.File

class ChunkStore(private val file: File) {
    fun loadAll(): List<ChunkEntry> {
        if (!file.exists()) return emptyList()
        return file.readLines().map { line ->
            val json = JSONObject(line)
            ChunkEntry(
                id = json.getString("id"),
                text = json.getString("text"),
                source = json.getString("source")
            )
        }
    }
}
