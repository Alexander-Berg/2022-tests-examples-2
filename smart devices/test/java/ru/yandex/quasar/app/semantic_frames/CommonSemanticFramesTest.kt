package ru.yandex.quasar.app.semantic_frames

import org.junit.Test
import ru.yandex.quasar.app.semantic_frames.common.MordoviaHomeScreenSemanticFrame
import ru.yandex.quasar.app.semantic_frames.common.RequestTechnicalSupportSemanticFrame

class CommonSemanticFramesTest {
    @Test
    fun given_requestTechnicalSupportSemanticFrame_when_serialize_then_serializedAsExpected() {
        val semanticFrame = RequestTechnicalSupportSemanticFrame()
        SemanticFrameTestsHelper.checkSemanticFrameSerialization(semanticFrame)
    }

    @Test
    fun given_mordoviaHomeScreenSemanticFrame_when_serialize_then_serializedAsExpected() {
        val semanticFrame = MordoviaHomeScreenSemanticFrame("123")
        SemanticFrameTestsHelper.checkSemanticFrameSerialization(semanticFrame)
    }
}
