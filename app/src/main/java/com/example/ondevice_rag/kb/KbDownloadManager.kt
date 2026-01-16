package com.example.ondevice_rag.kb

import android.content.Context
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.workDataOf
import com.example.ondevice_rag.worker.KbDownloadWorker

class KbDownloadManager(private val context: Context) {
    fun enqueue(scopeId: String, version: String, url: String, checksum: String) {
        val request = OneTimeWorkRequestBuilder<KbDownloadWorker>()
            .setInputData(
                workDataOf(
                    KbDownloadWorker.KEY_SCOPE_ID to scopeId,
                    KbDownloadWorker.KEY_VERSION to version,
                    KbDownloadWorker.KEY_URL to url,
                    KbDownloadWorker.KEY_CHECKSUM to checksum
                )
            )
            .build()
        WorkManager.getInstance(context).enqueue(request)
    }
}
