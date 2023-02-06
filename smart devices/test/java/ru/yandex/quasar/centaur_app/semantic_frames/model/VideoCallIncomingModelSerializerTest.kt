package ru.yandex.quasar.centaur_app.semantic_frames.model

import com.google.gson.Gson
import com.google.gson.GsonBuilder
import com.google.gson.JsonObject
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.core.IsEqual
import org.junit.Test
import ru.yandex.quasar.centaur_app.directives.models.videocalls.VideoCallProvider
import kotlin.random.Random

class VideoCallIncomingModelSerializerTest {
    private val gson: Gson = GsonBuilder()
        .registerTypeHierarchyAdapter(
            VideoCallContactData::class.java,
            VideoCallContactData.Serializer()
        )
        .create()

    private fun validateVideoCallIncomingModel(modelJson: JsonObject, model: VideoCallIncomingModel) {
        val provider = when (model.provider.value) {
            VideoCallProvider.TELEGRAM -> "telegram"
        }
        val providerJson = modelJson["provider"].asJsonObject
        assertThat(providerJson["enum_value"].asString, IsEqual(provider))

        val callIdJson = modelJson["call_id"].asJsonObject
        assertThat(callIdJson["string_value"].asString, IsEqual(model.callId.value))

        val userIdJson = modelJson["user_id"].asJsonObject
        assertThat(userIdJson["string_value"].asString, IsEqual(model.userId.value))

        val contactJson = modelJson["caller"].asJsonObject
        validateContactData(contactJson["contact_data"].asJsonObject, model.contact.contactData)
    }

    private fun validateContactData(contactDataJson: JsonObject, contactData: VideoCallContactData) {
        val prefix = when (contactData.provider) {
            VideoCallProvider.TELEGRAM -> "telegram"
        }
        assert(contactDataJson.has("${prefix}_contact_data"))
        val contact = contactDataJson["${prefix}_contact_data"].asJsonObject
        assertThat(contact["user_id"].asString, IsEqual(contactData.userId))
    }

    @Test
    fun `serialize telegram contact data`() {
        val contactData = VideoCallContactData(
            VideoCallProvider.TELEGRAM,
            Random.nextLong(0, Long.MAX_VALUE).toString()
        )
        val contactDataJson = gson.toJsonTree(contactData).asJsonObject
        validateContactData(contactDataJson, contactData)
    }

    @Test
    fun `serialize telegram call incoming`() {
        val videoCallIncomingModel = VideoCallIncomingModel(
            VideoCallProvider.TELEGRAM,
            Random.nextLong(0, Long.MAX_VALUE).toString(),
            Random.nextLong(0, Long.MAX_VALUE).toString(),
            Random.nextLong(0, Long.MAX_VALUE).toString()
        )

        val modelJson = gson.toJsonTree(videoCallIncomingModel).asJsonObject
        validateVideoCallIncomingModel(modelJson, videoCallIncomingModel)
    }
}
