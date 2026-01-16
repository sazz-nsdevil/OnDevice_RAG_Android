package com.example.ondevice_rag.data

class AuthRepository {
    fun login(username: String, password: String): UserSession {
        val scopes = listOf(
            SubjectScope(grade = "Grade 7", subject = "Science", kbVersion = "v1"),
            SubjectScope(grade = "Grade 7", subject = "Math", kbVersion = "v2")
        )
        return UserSession(
            userId = username,
            token = "fake-token",
            scopes = scopes
        )
    }
}
