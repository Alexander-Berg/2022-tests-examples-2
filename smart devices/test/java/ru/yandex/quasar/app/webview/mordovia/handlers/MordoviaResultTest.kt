package ru.yandex.quasar.app.webview.mordovia.handlers

import com.google.gson.Gson
import com.google.gson.stream.JsonWriter
import org.json.JSONException
import org.json.JSONObject
import org.junit.Assert
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.app.utils.json.toJson
import ru.yandex.quasar.app.webview.mordovia.handlers.MordoviaResult.Success.Companion.json
import ru.yandex.quasar.app.webview.mordovia.handlers.MordoviaResult.Success.Companion.raw

@RunWith(RobolectricTestRunner::class)
class MordoviaResultTest {

    @Test
    @Throws(JSONException::class)
    fun toJsonString() {
        val str = "Android ate an apple and said: \"It's fine!\""
        val result: MordoviaResult = raw(str)
        val expectedJson = JSONObject()
        expectedJson.put(MordoviaResult.Success.key, str)
        Assert.assertEquals(expectedJson.toString(), JSONObject(result.json).toString())
    }

    @Test
    @Throws(JSONException::class)
    fun toJsonJson() {
        val str = "Android ate an apple and said: \"It's fine!\""
        val json = JSONObject()
        json.put(MordoviaResult.Success.key, str)
        val result: MordoviaResult = json(json.toString())
        val expectedJson = JSONObject()
        expectedJson.put(MordoviaResult.Success.key, json)
        Assert.assertEquals(expectedJson.toString(), JSONObject(result.json).toString())
    }

    @Test
    @Throws(JSONException::class)
    fun error() {
        val error = MordoviaError("Some \"unique\" message")
        val result: MordoviaResult = MordoviaResult.Error(error)
        val expectedJson = JSONObject()
        expectedJson.put(MordoviaResult.Error.key, JSONObject(error.toJson()))
        Assert.assertEquals(expectedJson.toString(), JSONObject(result.json).toString())
    }

}
