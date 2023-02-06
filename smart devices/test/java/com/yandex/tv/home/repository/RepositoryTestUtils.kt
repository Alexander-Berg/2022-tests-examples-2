package com.yandex.tv.home.repository

import com.yandex.tv.home.content.MediaContentRepository
import com.yandex.tv.home.utils.SafeResult
import com.yandex.tv.home.utils.blockingSafeResult
import java.io.IOException
import java.io.InputStream
import java.nio.charset.StandardCharsets
import java.util.concurrent.Executor
import java.util.concurrent.TimeUnit
import java.util.concurrent.TimeoutException

inline fun <T> executeSyncRequest(
    waitSeconds: Long = 10,
    crossinline request: (MediaContentRepository.Callback<T>) -> Unit
): SafeResult<T> {
    return MediaContentRepository.createSingle<T> { request(it) }
        .timeout(waitSeconds, TimeUnit.SECONDS)
        .blockingSafeResult()
        .onFailure { return SafeResult.failure((it as? RuntimeException)?.cause ?: it) }
}

fun loadJSONFromResources(ins: InputStream): String {
    var json = ""
    try {
        val size = ins.available()
        val buffer = ByteArray(size)
        ins.read(buffer)
        ins.close()
        json = String(buffer, StandardCharsets.UTF_8)
    } catch (e: IOException) {
        e.printStackTrace()
    }
    return json
}

fun <T> createCallback(onSuccess: (T) -> Unit = {},
                       onError: (Exception) -> Unit = {}): MediaContentRepository.Callback<T> {
    return object: MediaContentRepository.Callback<T> {
        override fun onSuccess(data: T) {
            onSuccess(data)
        }

        override fun onError(error: Exception) {
            onError(error)
        }

    }
}

inline fun <T> repositoryExecuteBlocking(
    executor: Executor? = null,
    timeout: Long = 0,
    crossinline repositoryCall: (MediaContentRepository.Callback<T>) -> Unit,
    crossinline onSuccess: (T) -> Unit = {},
    crossinline onError: (Exception) -> Unit = {}
) {
    var executed = false
    var result: T? = null
    var exception: Exception? = null
    val repositoryCallback = object : MediaContentRepository.Callback<T> {
        override fun onSuccess(data: T) {
            result = data
            executed = true
        }

        override fun onError(error: Exception) {
            exception = error
            executed = true
        }
    }

    val startTime = System.currentTimeMillis()

    repositoryCall(repositoryCallback)

    while (!executed) {
        Thread.sleep(100)

        if (timeout > 0 && (System.currentTimeMillis() - startTime) > timeout) {
            executed = true
            exception = TimeoutException("timeout expired")
            break
        }
    }

    result?.let(onSuccess)
    exception?.let(onError)
}


