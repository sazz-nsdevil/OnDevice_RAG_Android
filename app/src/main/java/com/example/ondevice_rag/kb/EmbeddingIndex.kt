package com.example.ondevice_rag.kb

import java.io.File
import java.nio.ByteBuffer
import java.nio.ByteOrder
import kotlin.math.sqrt

class EmbeddingIndex(
    private val vectors: ShortArray,
    private val norms: FloatArray,
    val dimension: Int,
    val count: Int
) {
    fun topK(query: FloatArray, k: Int): List<ScoredChunk> {
        val queryNorm = sqrt(query.sumOf { it * it })
        val scored = ArrayList<ScoredChunk>(count)
        for (i in 0 until count) {
            var dot = 0f
            val base = i * dimension
            for (j in 0 until dimension) {
                val v = halfToFloat(vectors[base + j])
                dot += v * query[j]
            }
            val score = dot / (norms[i] * queryNorm + 1e-6f)
            scored.add(ScoredChunk(i, score))
        }
        return scored.sortedByDescending { it.score }.take(k)
    }

    companion object {
        fun load(file: File, dimension: Int, count: Int): EmbeddingIndex {
            val byteBuffer = ByteBuffer.wrap(file.readBytes()).order(ByteOrder.LITTLE_ENDIAN)
            val total = dimension * count
            val vectors = ShortArray(total)
            for (i in 0 until total) {
                vectors[i] = byteBuffer.short
            }
            val norms = FloatArray(count)
            for (i in 0 until count) {
                var sum = 0f
                val base = i * dimension
                for (j in 0 until dimension) {
                    val v = halfToFloat(vectors[base + j])
                    sum += v * v
                }
                norms[i] = sqrt(sum)
            }
            return EmbeddingIndex(vectors, norms, dimension, count)
        }

        fun halfToFloat(half: Short): Float {
            val h = half.toInt() and 0xFFFF
            val sign = h shr 15 and 0x00000001
            var exp = h shr 10 and 0x0000001F
            var mant = h and 0x000003FF
            if (exp == 0) {
                if (mant == 0) {
                    return if (sign == 0) 0f else -0f
                }
                while (mant and 0x00000400 == 0) {
                    mant = mant shl 1
                    exp -= 1
                }
                exp += 1
                mant = mant and 0x000003FF
            } else if (exp == 31) {
                return if (mant == 0) {
                    if (sign == 0) Float.POSITIVE_INFINITY else Float.NEGATIVE_INFINITY
                } else {
                    Float.NaN
                }
            }
            exp = exp + (127 - 15)
            val bits = (sign shl 31) or (exp shl 23) or (mant shl 13)
            return Float.fromBits(bits)
        }
    }
}

data class ScoredChunk(val index: Int, val score: Float)
