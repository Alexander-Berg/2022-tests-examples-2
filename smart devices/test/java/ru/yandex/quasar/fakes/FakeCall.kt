package ru.yandex.quasar.fakes

import okhttp3.Call
import okhttp3.Callback
import okhttp3.Request
import okhttp3.Response
import okio.Timeout
import java.io.IOException

class FakeCall(private val request: Request) : Call {

    private var cancelled = false
    private var enqueued = false
    private var callback: Callback? = null

    override fun enqueue(responseCallback: Callback) {
        enqueued = true
        callback = responseCallback
    }

    override fun isExecuted(): Boolean {
        throw UnsupportedOperationException()
    }

    override fun timeout(): Timeout {
        throw UnsupportedOperationException()
    }

    override fun clone(): Call {
        throw UnsupportedOperationException()
    }

    override fun isCanceled(): Boolean {
        return cancelled
    }

    override fun cancel() {
        cancelled = true
    }

    override fun request(): Request {
        return request
    }

    override fun execute(): Response {
        throw UnsupportedOperationException()
    }

    fun isEnqueued(): Boolean {
        return enqueued
    }

    fun getResponseCallback(): Callback? {
        return callback
    }

    fun onFailure(exc: IOException) {
        callback?.onFailure(this, exc)
    }

    fun onResponse(response: Response) {
        callback?.onResponse(this, response)
    }
}
