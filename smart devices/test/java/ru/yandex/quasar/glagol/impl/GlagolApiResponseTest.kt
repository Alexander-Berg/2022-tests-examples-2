package ru.yandex.quasar.glagol.impl

import org.apache.commons.io.IOUtils
import org.json.JSONException
import org.junit.Assert
import org.junit.Test
import ru.yandex.quasar.glagol.ResponseMessage
import ru.yandex.quasar.glagol.State
import java.io.IOException
import java.nio.charset.StandardCharsets

class GlagolApiResponseTest {

    @Test
    fun shouldParseGivenResponseWithoutError() {
        ConversationImpl.getReceivedMessageWrapper(
            getTestJson("/stateOnlyExample.1.0.json"),
            GsonFactory.receievedMessagesParser()
        )
        ConversationImpl.getReceivedMessageWrapper(
            getTestJson("/responseExample.1.0.json"),
            GsonFactory.receievedMessagesParser()
        )
    }

    @Test
    fun shouldParseResponseFields() {
        val wrapper = ConversationImpl.getReceivedMessageWrapper(
            getTestJson("/responseExample.1.0.json"),
            GsonFactory.receievedMessagesParser()
        )
        Assert.assertEquals("errorCode", wrapper.errorCode)
        Assert.assertEquals("errorText", wrapper.errorText)
        Assert.assertEquals(
            "9", wrapper.vinsResponse.getAsJsonObject("payload").getAsJsonObject("response")
                .getAsJsonObject("card")["text"].asString
        )
        Assert.assertNotNull(wrapper.vinsResponse.getAsJsonObject("header"))
        Assert.assertEquals(ResponseMessage.Status.SUCCESS, wrapper.status)
    }

    @Test
    fun shouldParseExtraFields() {
        val wrapper = ConversationImpl.getReceivedMessageWrapper(
            getTestJson("/responseExample.1.0.json"),
            GsonFactory.receievedMessagesParser()
        )
        Assert.assertNotNull(wrapper.extra)
        Assert.assertEquals("firmware-version", wrapper.extra["softwareVersion"])
    }

    @Test
    fun shouldParseSupportedFeatures() {
        val wrapper = ConversationImpl.getReceivedMessageWrapper(
            getTestJson("/stateOnlyExampleFull.json"),
            GsonFactory.receievedMessagesParser()
        )
        val message = MessageImpl(
            wrapper.id, wrapper.sentTime,
            wrapper.state, wrapper.status, wrapper.requestId, wrapper.extra,
            wrapper.supportedFeatures, wrapper.vinsResponse, wrapper.errorCode,
            wrapper.errorText, wrapper.errorTextLang
        )
        val features = message.supportedFeatures
        Assert.assertEquals(3, features.size.toLong())
        Assert.assertTrue(features.contains("muzpult"))
        Assert.assertTrue(features.contains("feature1"))
        Assert.assertTrue(features.contains("feature2"))
    }

    @Test
    fun parseNoSupportedFeatures() {
        val wrapper = ConversationImpl.getReceivedMessageWrapper(
            getTestJson("/responseExample.1.0.json"),
            GsonFactory.receievedMessagesParser()
        )
        val message = MessageImpl(
            wrapper.id, wrapper.sentTime,
            wrapper.state, wrapper.status, wrapper.requestId, wrapper.extra,
            wrapper.supportedFeatures, wrapper.vinsResponse, wrapper.errorCode,
            wrapper.errorText, wrapper.errorTextLang
        )
        val features = message.supportedFeatures
        Assert.assertTrue(features == null)
    }

    @Test
    fun parseAliceState() {
        val state = ConversationImpl.getReceivedMessageWrapper(
            getTestJson("/stateOnlyExampleFull.json"), GsonFactory.receievedMessagesParser()
        ).state!!

        val hdmi = state.hdmiState
        Assert.assertNotNull(hdmi)
        Assert.assertEquals(State.AliceState.IDLE, state.aliceState)
    }

    @Test
    fun parseHdmiState() {
        val hdmi = ConversationImpl.getReceivedMessageWrapper(
            getTestJson("/stateOnlyExampleFull.json"), GsonFactory.receievedMessagesParser()
        ).state.hdmiState!!

        Assert.assertNotNull(hdmi)
        Assert.assertFalse(hdmi.isCapable)
        Assert.assertTrue(hdmi.isPresent)
    }


    companion object {
        @Throws(IOException::class, JSONException::class)
        fun getTestJson(name: String): String {
            return IOUtils.toString(
                GlagolApiResponseTest::class.java.getResourceAsStream(name),
                StandardCharsets.UTF_8
            )
        }
    }
}
