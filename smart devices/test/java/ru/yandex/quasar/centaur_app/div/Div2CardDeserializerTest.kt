package ru.yandex.quasar.centaur_app.div

import com.google.gson.GsonBuilder
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.centaur_app.BaseTest
import ru.yandex.quasar.centaur_app.common.models.CentaurViewData
import ru.yandex.quasar.centaur_app.common.utils.Div2CardDeserializer

@RunWith(RobolectricTestRunner::class)
class Div2CardDeserializerTest: BaseTest() {
    @Test
    fun `when global templates are provided, parse it` () {
        val data = """
{
    "body": {
        "card": {
            "states": [],
            "log_id": "iot-web"
        },
        "templates": {}
    },
    "global_templates": {
        "vault_images": {
            "body": {
                "back_image": {}
            }
        }
    }
}
        """.trimIndent()
        val gson = GsonBuilder()
            .registerTypeAdapter(
                CentaurViewData.Div2Card::class.java,
                Div2CardDeserializer()
            )
            .create()
        val card = gson.fromJson(data, CentaurViewData.Div2Card::class.java)
        assertEquals(card.globalTemplates!!, "{\"vault_images\":{\"body\":{\"back_image\":{}}}}")
    }

    @Test
    fun `when div2 provided as string_body, parse it correctly` () {
        val data = """
{
    "string_body": "{\"card\": {\"states\": [],\"log_id\": \"iot-web\"},\"templates\": {}}",
    "global_templates": {
        "vault_images": {
            "string_body": "{\"back_image\": {}}"
        }
    }
}
        """.trimIndent()
        val gson = GsonBuilder()
            .registerTypeAdapter(
                CentaurViewData.Div2Card::class.java,
                Div2CardDeserializer()
            )
            .create()
        val card = gson.fromJson(data, CentaurViewData.Div2Card::class.java)
        assertEquals(card.globalTemplates!!, "{\"vault_images\":{\"string_body\":\"{\\\"back_image\\\": {}}\"}}")
        assertEquals(card.stringBody!!, "{\"card\": {\"states\": [],\"log_id\": \"iot-web\"},\"templates\": {}}")
    }
}
