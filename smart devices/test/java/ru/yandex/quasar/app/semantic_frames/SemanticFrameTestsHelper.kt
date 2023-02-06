package ru.yandex.quasar.app.semantic_frames

import com.google.gson.Gson
import com.google.gson.GsonBuilder
import com.google.gson.JsonObject
import org.junit.Assert

object SemanticFrameTestsHelper {
    val gson: Gson =
        GsonBuilder()
            .registerTypeHierarchyAdapter(SemanticFrame::class.java, SemanticFrameGsonSerializer())
            .create()

    fun createSemanticFrameJsonObject(semanticFrame: SemanticFrame): JsonObject {
        val semanticFrameObj = JsonObject()
        semanticFrameObj.add(
            semanticFrame.name,
            if (semanticFrame.data == null) JsonObject() else gson.toJsonTree(semanticFrame.data)
        )
        val analyticsObj = JsonObject()
        analyticsObj.addProperty("product_scenario", semanticFrame.analytics.productScenario)
        analyticsObj.addProperty("origin", semanticFrame.analytics.origin)
        analyticsObj.addProperty("purpose", semanticFrame.analytics.purpose)
        if (semanticFrame.analytics.originInfo != null) {
            analyticsObj.addProperty("origin_info", gson.toJson(semanticFrame.analytics.originInfo))
        }
        val result = JsonObject()
        result.add("typed_semantic_frame", semanticFrameObj)
        result.add("analytics", analyticsObj)
        return result
    }

    fun createSemanticFrameWrapperJsonObject(semanticFrameWrapper: SemanticFrameWrapper): JsonObject {
        val result = JsonObject()
        result.addProperty("type", "server_action")
        result.addProperty("name", "@@mm_semantic_frame")
        result.add("payload", createSemanticFrameJsonObject(semanticFrameWrapper.data as SemanticFrame))
        return result
    }

    fun checkSemanticFrameSerialization(semanticFrame: SemanticFrame) {
        val semanticFrameObj = createSemanticFrameJsonObject(semanticFrame)
        Assert.assertEquals(semanticFrameObj, gson.toJsonTree(semanticFrame))

        val semanticFrameWrapper = SemanticFrameWrapper(semanticFrame)
        val semanticFrameWrapperObj = createSemanticFrameWrapperJsonObject(semanticFrameWrapper)
        Assert.assertEquals(semanticFrameWrapperObj, gson.toJsonTree(semanticFrameWrapper))
    }
}
