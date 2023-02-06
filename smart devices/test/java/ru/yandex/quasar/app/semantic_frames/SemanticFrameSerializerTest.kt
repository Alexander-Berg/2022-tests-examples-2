package ru.yandex.quasar.app.semantic_frames

import com.google.gson.JsonObject
import org.junit.Test
import ru.yandex.quasar.app.semantic_frames.SemanticFrameTestsHelper.checkSemanticFrameSerialization
import ru.yandex.quasar.app.semantic_frames.SemanticFrameTestsHelper.gson

class SemanticFrameSerializerTest {
    @Test
    fun given_semanticFrameWithoutData_when_serialize_then_serializedWithEmptyBody() {
        val semanticFrame = SemanticFrame("frame_name")
        semanticFrame.analytics = SemanticFrameAnalytics("scenario", "origin", "purpose")

        checkSemanticFrameSerialization(semanticFrame)
    }

    @Test
    fun given_semanticFrameWithData_when_serialize_then_serializedWithBody() {
        val semanticFrame = SemanticFrame("frame_name")
        val data = JsonObject()
        data.addProperty("data", "123")
        semanticFrame.data = data
        semanticFrame.analytics = SemanticFrameAnalytics("scenario", "origin", "purpose")

        checkSemanticFrameSerialization(semanticFrame)
    }

    @Test(expected = UninitializedPropertyAccessException::class)
    fun given_semanticFrameWithoutAnalytics_when_serialize_then_exception() {
        val semanticFrame = SemanticFrame("frame_name")
        gson.toJson(semanticFrame)
    }
}
