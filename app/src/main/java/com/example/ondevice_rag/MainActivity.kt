package com.example.ondevice_rag

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavGraphBuilder
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.example.ondevice_rag.kb.KbDownloadManager
import com.example.ondevice_rag.ui.MainViewModel
import com.example.ondevice_rag.ui.MainViewModelFactory
import com.example.ondevice_rag.ui.screens.ChatScreen
import com.example.ondevice_rag.ui.screens.LoginScreen
import com.example.ondevice_rag.ui.screens.ScopeSelectionScreen
import com.example.ondevice_rag.ui.theme.OnDeviceRagTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            val context = LocalContext.current
            val viewModel: MainViewModel = viewModel(factory = MainViewModelFactory(context))
            val state by viewModel.uiState.collectAsState()
            val navController = rememberNavController()
            val downloadManager = KbDownloadManager(context)

            OnDeviceRagTheme(darkTheme = isSystemInDarkTheme()) {
                NavHost(navController = navController, startDestination = "login") {
                    addLogin(viewModel, navController)
                    composable("scopes") {
                        ScopeSelectionScreen(
                            scopes = state.session?.scopes.orEmpty(),
                            selected = state.selectedScope,
                            onSelect = { viewModel.selectScope(it) },
                            onDownload = { scope ->
                                val request = viewModel.buildDownloadRequest(scope)
                                viewModel.setDownloading(true)
                                downloadManager.enqueue(
                                    scopeId = request.scopeId,
                                    version = request.version,
                                    url = request.url,
                                    checksum = request.checksum
                                )
                            },
                            onContinue = { navController.navigate("chat") }
                        )
                    }
                    composable("chat") {
                        val title = state.selectedScope?.let { "${it.grade} · ${it.subject}" } ?: "Chat"
                        ChatScreen(
                            title = title,
                            messages = state.messages,
                            onSend = { viewModel.sendMessage(it) }
                        )
                    }
                }
            }
        }
    }
}

private fun NavGraphBuilder.addLogin(viewModel: MainViewModel, navController: androidx.navigation.NavHostController) {
    composable("login") {
        LoginScreen { username, password ->
            viewModel.login(username, password)
            navController.navigate("scopes") {
                popUpTo("login") { inclusive = true }
            }
        }
    }
}
