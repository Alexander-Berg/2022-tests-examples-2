package ru.yandex.quasar.centaur_app.div

import org.json.JSONObject
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.Assert.assertEquals
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.centaur_app.BaseTest
import ru.yandex.quasar.centaur_app.FakeMetricaReporter

@RunWith(RobolectricTestRunner::class)
class ShowViewInfoJsonMapperTest: BaseTest() {

    @Test
    fun `parse global templates when provided` () {
        val showViewInfo = ShowViewInfo.Companion.parseDirectivePayload(JSONObject(
            """
{
    "div2_card": {
        "body": {
            "card": {
                "log_id": "global_templates_card",
                "states": []
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
    },
    "layer": {
        "dialog": {}
    }
}
            """.trimIndent()
        ), FakeMetricaReporter())

        assertEquals(showViewInfo!!.card.providedGlobalTemplates.size, 1)
        assert(showViewInfo!!.card.providedGlobalTemplates.get("vault_images") != null)
        assert(showViewInfo!!.card.providedGlobalTemplates.get("vault_images").toString() == "{\"back_image\":{}}")
    }
}
