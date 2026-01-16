package com.example.ondevice_rag.ui

import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.example.ondevice_rag.kb.KbPackageManager

class MainViewModelFactory(private val context: Context) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(MainViewModel::class.java)) {
            val packageManager = KbPackageManager(context)
            @Suppress("UNCHECKED_CAST")
            return MainViewModel(packageManager = packageManager) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}
