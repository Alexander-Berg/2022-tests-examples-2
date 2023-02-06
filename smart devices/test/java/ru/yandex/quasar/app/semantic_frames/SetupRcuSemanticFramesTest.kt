package ru.yandex.quasar.app.semantic_frames

import org.junit.Assert.assertEquals
import org.junit.Test
import ru.yandex.quasar.app.semantic_frames.SemanticFrameTestsHelper.gson
import ru.yandex.quasar.app.semantic_frames.rcu.*

class SetupRcuSemanticFramesTest {
    @Test
    fun given_setupRcuSemanticFrame_when_serialize_then_serializedAsExpected() {
        val statuses = SetupRcuStatus.SetupRcuStatusValue.values()
        for (status in statuses) {
            val semanticFrame = SetupRcuSemanticFrame(status)
            SemanticFrameTestsHelper.checkSemanticFrameSerialization(semanticFrame)
        }
    }

    @Test
    fun given_setupRcuAutoSemanticFrame_when_serialize_then_serializedAsExpected() {
        val statuses = SetupRcuStatus.SetupRcuStatusValue.values()
        for (status in statuses) {
            val semanticFrame = SetupRcuAutoSemanticFrame(status)
            SemanticFrameTestsHelper.checkSemanticFrameSerialization(semanticFrame)
        }
    }

    @Test
    fun given_setupRcuCheckSemanticFrame_when_serialize_then_serializedAsExpected() {
        val statuses = SetupRcuStatus.SetupRcuStatusValue.values()
        for (status in statuses) {
            val semanticFrame = SetupRcuCheckSemanticFrame(status)
            SemanticFrameTestsHelper.checkSemanticFrameSerialization(semanticFrame)
        }
    }

    @Test
    fun given_setupRcuAdvancedSemanticFrame_when_serialize_then_serializedAsExpected() {
        val statuses = SetupRcuStatus.SetupRcuStatusValue.values()
        for (status in statuses) {
            val semanticFrame = SetupRcuAdvancedSemanticFrame(status)
            SemanticFrameTestsHelper.checkSemanticFrameSerialization(semanticFrame)
        }
    }

    @Test
    fun given_setupRcuManualStartSemanticFrame_when_serialize_then_serializedAsExpected() {
        val semanticFrame = SetupRcuManualStartSemanticFrame()
        SemanticFrameTestsHelper.checkSemanticFrameSerialization(semanticFrame)
    }

    @Test
    fun given_setupRcuAutoStartSemanticFrame_when_serialize_then_serializedAsExpected() {
        val tvModel = "testTvModel"
        val semanticFrame = SetupRcuAutoStartSemanticFrame(tvModel)
        SemanticFrameTestsHelper.checkSemanticFrameSerialization(semanticFrame)
    }

    @Test
    fun given_setupRcuFrameStatus_when_serialize_then_serializedWithEnumValue() {
        val statuses = SetupRcuStatus.SetupRcuStatusValue.values()
        for (status in statuses) {
            val frameStatus = SetupRcuSemanticFrameStatus(status)
            val frameStatusObj = gson.toJsonTree(frameStatus).asJsonObject
            assert(frameStatusObj.has("status"))
            val statusObj = frameStatusObj["status"].asJsonObject
            assert(statusObj.has("enum_value"))
            assertEquals(status.name, statusObj["enum_value"].asString)
        }
    }

    @Test
    fun given_setupRcuTvModel_when_serialize_then_serializedWithEnumValue() {
        val tvModels = listOf("SomeTvModel", "some_tv_model", "tv model with spaces", "модель телевизора", "")
        for (model in tvModels) {
            val frameModel = SetupRcuSemanticFrameTvModel(model)
            val frameModelObj = gson.toJsonTree(frameModel).asJsonObject
            assert(frameModelObj.has("tv_model"))
            val modelObj = frameModelObj["tv_model"].asJsonObject
            assert(modelObj.has("string_value"))
            assertEquals(model, modelObj["string_value"].asString)
        }
    }
}
