package ru.yandex.quasar.app.webview.mordovia.handlers

import com.yandex.alicekit.core.utils.Assert.assertEquals
import org.json.JSONObject
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.app.utils.json.toJson

@RunWith(RobolectricTestRunner::class)
class MordoviaErrorTest {

    @Test
    fun mordoviaErrorToJson() {
        val message = "Some error message: \n, \t, \", \r, '@$%^&!#"
        val error = MordoviaError(message).toJson()
        val expectedJson = JSONObject()
        expectedJson.put(MordoviaError.messageKey, message)
        expectedJson.put(MordoviaError.codeKey, MordoviaError.internalErrorCode)
        assertEquals(expectedJson.toString(), JSONObject(error).toString())
    }
}
