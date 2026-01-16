package com.example.ondevice_rag.data

data class KbDownloadRequest(
    val scopeId: String,
    val version: String,
    val url: String,
    val checksum: String
)
