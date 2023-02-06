package ru.yandex.quasar.app.services

import com.google.gson.Gson
import com.google.gson.JsonObject
import org.junit.Assert

object ServerActionTestsHelper {

    val gson: Gson = Gson()

    fun createServerActionJsonObject(serverAction: ServerAction): JsonObject {
        val result = JsonObject()
        result.addProperty("name", serverAction.name)
        result.addProperty("type", serverAction.type)
        result.add("payload", gson.toJsonTree(serverAction.data))
        if (serverAction.ignoreAnswer != null) {
            result.addProperty("ignore_answer", serverAction.ignoreAnswer)
        }
        return result
    }

    fun checkServerActionSerialization(serverAction: ServerAction) {
        val serverActionObj = createServerActionJsonObject(serverAction)
        Assert.assertEquals(serverActionObj, gson.toJsonTree(serverAction))
    }
}
