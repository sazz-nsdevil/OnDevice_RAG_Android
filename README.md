(By: Sujal Neupane)
# **Technical Update: Android LLM Integration Status** 

## **1. The Problem: Direct `llama-cpp` Build Failure**
Our attempt to compile and run `llama-cpp` modules directly within the Android environment was unsuccessful. The process was automatically terminated by the system (**SIGKILL**) during the build phase.

* **Cause:** The Android Emulator/Virtual Machine has a strict RAM ceiling.
* **The Conflict:** Compiling heavy C++ modules like `llama-cpp` requires a massive amount of "Peak RAM" to handle parallel tasks. When the compiler exceeded the Emulator's allowed memory, the OS killed the process to prevent a system-wide freeze.
* **Conclusion:** Building the engine inside the app environment is too resource-heavy for standard Android development tools and would likely lead to frequent "Force Close" errors for our end users.

---

## **2. The Solution: "Sidecar" Architecture via `llamafile`**
To ensure stability, we are pivoting to a **Sidecar Architecture**. Instead of forcing the AI engine inside our app, we will run it as a separate, lightweight background service (Local API).

### **Comparison of Approaches**

| Feature | Direct Integration (Failed) | llamafile Sidecar (Proposed) |
| :--- | :--- | :--- |
| **Stability** | **High Crash Risk:** One memory spike kills the whole app. | **Isolated:** If the AI engine resets, the app stays open. |
| **Build Time** | **Unstable:** Requires massive RAM for C++ compilation. | **Instant:** Uses pre-compiled, optimized binaries. |
| **Development** | **Fragile:** Deeply tied to NDK/JNI dependencies. | **Flexible:** Uses standard HTTP/JSON (OpenAI-compatible). |
| **Performance** | Throttled by Emulator/JVM overhead. | **Native Speed:** Runs directly on the Linux kernel. |

---

## **3. Strategic Path Forward**
We will implement the RAG (Retrieval-Augmented Generation) logic using a **Decoupled Workflow**:

1.  **Context Retrieval:** Our main app fetches data from our existing external endpoint.
2.  **Prompt Construction:** The app packages the retrieved data and the user's question into a single prompt.
3.  **Local Inference:** The app sends this text to the `llamafile` background service via a local HTTP request (`localhost:8080`).

**This approach guarantees a 100% private, local AI experience without the build-time or runtime memory crashes experienced previously.**


![Project Screenshot](OnDevice_RAG_HighLevel_.png)
