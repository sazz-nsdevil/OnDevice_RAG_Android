package com.example.ondevice_rag.kb

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.dataStore by preferencesDataStore(name = "kb_metadata")

class KbMetadataStore(private val context: Context) {
    private fun keyForScope(scopeId: String) = stringPreferencesKey("kb_version_$scopeId")

    fun versionFlow(scopeId: String): Flow<String?> {
        return context.dataStore.data.map { prefs -> prefs[keyForScope(scopeId)] }
    }

    suspend fun setVersion(scopeId: String, version: String) {
        context.dataStore.edit { prefs ->
            prefs[keyForScope(scopeId)] = version
        }
    }
}
