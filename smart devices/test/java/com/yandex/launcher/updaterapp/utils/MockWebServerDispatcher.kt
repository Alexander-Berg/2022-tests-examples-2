package com.yandex.launcher.updaterapp.utils

import com.yandex.launcher.logger.KLogger
import java.util.ArrayDeque

import okhttp3.mockwebserver.Dispatcher
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.RecordedRequest

class MockWebServerDispatcher : Dispatcher() {

    private val items = HashMap<String, ArrayDeque<Item>>()
    private val permanentItems = HashMap<String, Item>()

    @Throws(InterruptedException::class)
    override fun dispatch(request: RecordedRequest): MockResponse {
        val item = permanentItems[request.path] ?: items[request.path]?.poll()
        val response = if (item != null) {
            MockResponse().setResponseCode(item.code).setBody(item.body)
        } else {
            MockResponse().setResponseCode(500)
        }

        KLogger.d("MockWebServerDispatcher") { "Response $response, for ${request.path}" }
        return response
    }

    @JvmOverloads
    fun enqueue(path: String, code: Int, body: String, permanent: Boolean = false) {
        val item = Item(code, body)
        val correctedPath = if (path.startsWith("/")) {
            path
        } else {
            "/$path"
        }
        val existingRequests = items[correctedPath]
        val requests: ArrayDeque<Item> = if (existingRequests != null) {
            existingRequests.add(item)
            existingRequests
        } else {
            val array = ArrayDeque<Item>()

            array.add(item)
            array
        }

        KLogger.d("MockWebServerDispatcher") { "Response $code, added for $correctedPath" }

        items[correctedPath] = requests

        if (permanent) {
            permanentItems[correctedPath] = item
        }
    }

    @JvmOverloads
    fun clear(path: String = "") {
        if (path.isEmpty()) {
            permanentItems.clear()
            items.clear()
            return
        }

        val correctedPath = if (path.startsWith("/")) {
            path
        } else {
            "/$path"
        }

        items.remove(correctedPath)
        permanentItems.remove(correctedPath)
    }

    private class Item(val code: Int, val body: String)
}
