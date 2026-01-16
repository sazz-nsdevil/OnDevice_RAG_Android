package com.example.ondevice_rag.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.ondevice_rag.data.AuthRepository
import com.example.ondevice_rag.data.ChatMessage
import com.example.ondevice_rag.data.KbDownloadRequest
import com.example.ondevice_rag.data.Role
import com.example.ondevice_rag.data.SubjectScope
import com.example.ondevice_rag.kb.KbPackageManager
import com.example.ondevice_rag.kb.RetrievalEngine
import com.example.ondevice_rag.llama.LlamaManager
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.util.UUID

class MainViewModel(
    private val authRepository: AuthRepository = AuthRepository(),
    private val llamaManager: LlamaManager = LlamaManager(),
    private val packageManager: KbPackageManager
) : ViewModel() {

    private val _uiState = MutableStateFlow(MainUiState())
    val uiState: StateFlow<MainUiState> = _uiState.asStateFlow()

    fun login(username: String, password: String) {
        val session = authRepository.login(username, password)
        _uiState.update { it.copy(session = session, selectedScope = session.scopes.firstOrNull()) }
    }

    fun selectScope(scope: SubjectScope) {
        _uiState.update { it.copy(selectedScope = scope) }
    }

    fun buildDownloadRequest(scope: SubjectScope): KbDownloadRequest {
        val scopeId = packageManager.scopeId(scope.grade, scope.subject)
        val url = "https://cdn.example.com/kb/$scopeId/${scope.kbVersion}.zip"
        return KbDownloadRequest(
            scopeId = scopeId,
            version = scope.kbVersion,
            url = url,
            checksum = "replace-with-manifest-checksum"
        )
    }

    fun setDownloading(value: Boolean) {
        _uiState.update { it.copy(isDownloading = value) }
    }

    fun appendUserMessage(text: String) {
        val message = ChatMessage(UUID.randomUUID().toString(), Role.USER, text)
        _uiState.update { it.copy(messages = it.messages + message) }
    }

    fun appendAssistantMessage(text: String) {
        val message = ChatMessage(UUID.randomUUID().toString(), Role.ASSISTANT, text)
        _uiState.update { it.copy(messages = it.messages + message) }
    }

    fun streamAssistantTokens(tokens: String) {
        _uiState.update { state ->
            val messages = state.messages.toMutableList()
            val last = messages.lastOrNull()
            if (last == null || last.role != Role.ASSISTANT) {
                messages.add(ChatMessage(UUID.randomUUID().toString(), Role.ASSISTANT, tokens))
            } else {
                messages[messages.lastIndex] = last.copy(content = last.content + tokens)
            }
            state.copy(messages = messages)
        }
    }

    fun sendMessage(text: String) {
        val scope = _uiState.value.selectedScope ?: return
        val scopeId = packageManager.scopeId(scope.grade, scope.subject)
        appendUserMessage(text)
        viewModelScope.launch {
            val retrieval = RetrievalEngine(llamaManager, packageManager)
            val chunks = retrieval.retrieve(scopeId, text, k = 4)
            val context = chunks.joinToString("\n\n") { "- ${it.text}" }
            val prompt = """
                You are a helpful tutor for ${scope.grade} ${scope.subject}.
                Use the provided context to answer clearly and briefly.

                Context:
                $context

                Question: $text
                Answer:
            """.trimIndent()
            llamaManager.generate(prompt).collect { token ->
                streamAssistantTokens(token)
            }
        }
    }
}

data class MainUiState(
    val session: com.example.ondevice_rag.data.UserSession? = null,
    val selectedScope: SubjectScope? = null,
    val messages: List<ChatMessage> = emptyList(),
    val isDownloading: Boolean = false
)
