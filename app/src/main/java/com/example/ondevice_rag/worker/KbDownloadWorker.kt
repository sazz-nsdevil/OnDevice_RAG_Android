package com.example.ondevice_rag.worker

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.example.ondevice_rag.kb.KbMetadataStore
import com.example.ondevice_rag.kb.KbPackageManager
import com.example.ondevice_rag.util.sha256
import com.example.ondevice_rag.util.unzip
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.File

class KbDownloadWorker(
    appContext: Context,
    params: WorkerParameters
) : CoroutineWorker(appContext, params) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        val url = inputData.getString(KEY_URL) ?: return@withContext Result.failure()
        val checksum = inputData.getString(KEY_CHECKSUM) ?: return@withContext Result.failure()
        val scopeId = inputData.getString(KEY_SCOPE_ID) ?: return@withContext Result.failure()
        val version = inputData.getString(KEY_VERSION) ?: return@withContext Result.failure()

        val client = OkHttpClient()
        val request = Request.Builder().url(url).build()
        val zipFile = File(applicationContext.cacheDir, "kb_$scopeId.zip")

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                return@withContext Result.retry()
            }
            response.body?.byteStream()?.use { input ->
                zipFile.outputStream().use { output ->
                    input.copyTo(output)
                }
            } ?: return@withContext Result.retry()
        }

        val actualChecksum = zipFile.sha256()
        if (!actualChecksum.equals(checksum, ignoreCase = true)) {
            zipFile.delete()
            return@withContext Result.failure()
        }

        val packageManager = KbPackageManager(applicationContext)
        val targetDir = packageManager.packageDir(scopeId)
        if (targetDir.exists()) {
            targetDir.deleteRecursively()
        }
        unzip(zipFile, targetDir)

        KbMetadataStore(applicationContext).setVersion(scopeId, version)
        zipFile.delete()
        Result.success()
    }

    companion object {
        const val KEY_URL = "kb_url"
        const val KEY_CHECKSUM = "kb_checksum"
        const val KEY_SCOPE_ID = "kb_scope_id"
        const val KEY_VERSION = "kb_version"
    }
}
