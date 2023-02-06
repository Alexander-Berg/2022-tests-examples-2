package com.yandex.io.sdk.ipc

import android.os.Build
import com.yandex.io.sdk.proto.AudioSdkProto
import com.yandex.io.sdk.proto.BinderProto
import com.yandex.io.sdk.utils.BinderResponseHelper
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.M])
class QuasarBinderTest {

    private lateinit var binderA: TestableQuasarBinder
    private lateinit var binderB: TestableQuasarBinder

    @Before
    fun setUp() {
        binderA = TestableQuasarBinder()
        binderB = TestableQuasarBinder()
    }

    @After
    fun tearDown() {
        binderA.disconnect(binderB)
        binderB.disconnect(binderA)
    }

    @Test
    fun givenQuasarBinder_whenSendIsCalled_thenBinderReceivesMessage() {
        val message = AudioSdkProto.MusicPlayerState.getDefaultInstance()

        binderA.send(message.toByteArray(), binderB)
        assertEquals(1, binderA.onIncomingMessageCalls)
        assertEquals(listOf(message to binderB), binderA.incomingMessages)
    }

    @Test
    fun givenQuasarBinder_whenWaitForResponse_thenBinderReturnsSuccess() {
        val message = AudioSdkProto.MusicPlayerState.getDefaultInstance()

        val response = binderA.send(message.toByteArray(), binderB)
        val parsed = BinderProto.BinderResponse.parseFrom(response)

        assertEquals(BinderResponseHelper.success, parsed)
    }

    @Test
    fun givenQuasarBinder_whenConnectIsCalled_thenBinderReceivesOnConnected() {
        binderA.connect(binderB)
        assertEquals(1, binderA.onConnectedCalls)
        assertEquals(binderB, binderA.connected)
    }

    @Test
    fun givenConnectedQuasarBinder_whenDisconnectIsCalled_thenBinderReceivesOnDisconnected() {
        binderA.connect(binderB)
        binderA.disconnect(binderB)
        assertEquals(1, binderA.onConnectedCalls)
        assertEquals(1, binderA.onDisconnectedCalls)
        assertNull(binderA.connected)
    }

    @Test
    fun givenQuasarBinder_whenDuplicateConnectCalls_thenBinderReceivesTwoCallbacks() {
        binderA.connect(binderB)
        binderA.connect(binderB)
        assertEquals(2, binderA.onConnectedCalls)
        assertEquals(binderB, binderA.connected)
    }

    @Test
    fun givenQuasarBinder_whenDuplicateConnectCalls_thenBinderReceivesSingleCallback() {
        binderA.connect(binderB)
        binderA.disconnect(binderB)
        binderA.disconnect(binderB)
        assertEquals(1, binderA.onDisconnectedCalls)
        assertNull(binderA.connected)
    }

    @Test
    fun givenQuasarBinder_whenConnected_thenCanReceiveBroadcast() {
        val message = AudioSdkProto.MusicPlayerState.getDefaultInstance()

        binderB.connect(binderA)
        binderB.broadcast(message.toByteArray())
        assertEquals(1, binderA.onIncomingMessageCalls)
        assertEquals(listOf(message to binderB), binderA.incomingMessages)
    }

    @Test
    fun givenQuasarBinder_whenDisconnected_thenCannotReceiveBroadcast() {
        val message = AudioSdkProto.MusicPlayerState.getDefaultInstance()

        binderA.connect(binderB)
        binderA.disconnect(binderB)

        binderB.broadcast(message.toByteArray())
        assertEquals(0, binderA.onIncomingMessageCalls)
        assert(binderA.incomingMessages.isEmpty())
    }

    private class TestableQuasarBinder() : QuasarBinder.Stub<AudioSdkProto.MusicPlayerState, BinderProto.BinderResponse>(
        incomingMessageParser = AudioSdkProto.MusicPlayerState::parseFrom
    ) {
        val incomingMessages = mutableListOf<Pair<AudioSdkProto.MusicPlayerState, QuasarBinder>>()
        var connected: QuasarBinder? = null

        var onConnectedCalls = 0
        var onDisconnectedCalls = 0
        var onIncomingMessageCalls = 0

        override fun onConnected(peer: QuasarBinder) {
            connected = peer
            onConnectedCalls++
        }

        override fun onDisconnected(peer: QuasarBinder) {
            connected = null
            onDisconnectedCalls++
        }

        override fun onIncomingMessage(message: AudioSdkProto.MusicPlayerState, sender: QuasarBinder): BinderProto.BinderResponse {
            incomingMessages.add(message to sender)
            onIncomingMessageCalls++
            return BinderResponseHelper.success
        }

    }
}
