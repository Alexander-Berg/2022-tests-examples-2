package ru.yandex.quasar.app.services

import com.google.gson.JsonObject
import org.junit.Test
import ru.yandex.quasar.app.services.ServerActionTestsHelper.checkServerActionSerialization

class ServerActionSerializerTest {

    @Test
    fun given_serverActionWithData_when_serialize_then_serializedWithBody() {
        val serverAction = ServerAction("action_name")
        val data = JsonObject()
        data.addProperty("data", "123")
        serverAction.data = data
        checkServerActionSerialization(serverAction)
    }

    @Test
    fun given_serverActionWithIgnoreAnswer_when_serialize_then_serializedWithIgnoreAnswer() {
        val serverAction = ServerAction("action_name")
        val data = JsonObject()
        data.addProperty("data", "234")
        serverAction.data = data
        serverAction.ignoreAnswer = true
        checkServerActionSerialization(serverAction)
    }
}
