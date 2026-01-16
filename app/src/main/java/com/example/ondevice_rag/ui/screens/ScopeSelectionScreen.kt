package com.example.ondevice_rag.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.ondevice_rag.data.SubjectScope

@Composable
fun ScopeSelectionScreen(
    scopes: List<SubjectScope>,
    selected: SubjectScope?,
    onSelect: (SubjectScope) -> Unit,
    onDownload: (SubjectScope) -> Unit,
    onContinue: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(20.dp),
        verticalArrangement = Arrangement.Top
    ) {
        Text(text = "Choose subject", style = MaterialTheme.typography.headlineSmall)
        Spacer(modifier = Modifier.height(12.dp))
        LazyColumn(
            contentPadding = PaddingValues(vertical = 8.dp)
        ) {
            items(scopes) { scope ->
                Card(
                    modifier = Modifier
                        .padding(bottom = 12.dp)
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp)
                    ) {
                        Text(text = "${scope.grade} · ${scope.subject}")
                        Text(text = "KB ${scope.kbVersion}")
                        Spacer(modifier = Modifier.height(8.dp))
                        Button(onClick = { onSelect(scope) }) {
                            Text(if (scope == selected) "Selected" else "Select")
                        }
                        Spacer(modifier = Modifier.height(8.dp))
                        Button(onClick = { onDownload(scope) }) {
                            Text("Download KB")
                        }
                    }
                }
            }
        }
        Spacer(modifier = Modifier.height(12.dp))
        Button(onClick = onContinue, enabled = selected != null) {
            Text("Open chat")
        }
    }
}
