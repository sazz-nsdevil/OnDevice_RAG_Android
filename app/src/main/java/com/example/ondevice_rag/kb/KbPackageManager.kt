package com.example.ondevice_rag.kb

import android.content.Context
import java.io.File

class KbPackageManager(private val context: Context) {
    fun scopeId(grade: String, subject: String): String {
        return grade.lowercase().replace(" ", "_") + "__" + subject.lowercase().replace(" ", "_")
    }

    fun packageDir(scopeId: String): File {
        return File(context.filesDir, "kb/$scopeId")
    }

    fun manifestFile(scopeId: String): File {
        return File(packageDir(scopeId), "manifest.json")
    }

    fun embeddingsFile(scopeId: String): File {
        return File(packageDir(scopeId), "embeddings.f16")
    }

    fun chunksFile(scopeId: String): File {
        return File(packageDir(scopeId), "chunks.jsonl")
    }
}
