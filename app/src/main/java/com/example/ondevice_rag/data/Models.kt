package com.example.ondevice_rag.data

data class SubjectScope(
    val grade: String,
    val subject: String,
    val kbVersion: String
)

data class UserSession(
    val userId: String,
    val token: String,
    val scopes: List<SubjectScope>
)

data class ChatMessage(
    val id: String,
    val role: Role,
    val content: String
)

enum class Role {
    USER,
    ASSISTANT,
    SYSTEM
}
