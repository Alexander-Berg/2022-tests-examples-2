package ru.yandex.quasar.app.rcu.voice

import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothGatt
import android.bluetooth.BluetoothGattCharacteristic
import android.os.Handler
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.argumentCaptor
import org.mockito.kotlin.clearInvocations
import org.mockito.kotlin.mock
import org.mockito.kotlin.never
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import ru.yandex.quasar.app.rcu.observable.RcuConnectionObservable
import ru.yandex.quasar.app.rcu.sender.RcuManager
import ru.yandex.quasar.app.rcu.update.RcuUpdateManager
import ru.yandex.quasar.fakes.FakeMetricaReporter
import ru.yandex.quasar.protobuf.ModelObjects.EmptyMessage
import ru.yandex.quasar.protobuf.ModelObjects.RcuVoiceEvent
import ru.yandex.quasar.protobuf.QuasarProto.QuasarMessage
import ru.yandex.quasar.shadows.ShadowThreadUtil
import ru.yandex.quasar.transport.QuasarServer

@RunWith(RobolectricTestRunner::class)
@Config(
    shadows = [ShadowThreadUtil::class],
    instrumentedPackages = ["ru.yandex.quasar.concurrency"]
)
class RcuVoiceServerTest {
    private val mockRcuManager: RcuManager = mock()
    private val mockRcuUpdateManager: RcuUpdateManager = mock()
    private val mockServer: QuasarServer = mock()
    private val mockBluetoothDevice: BluetoothDevice = mock()
    private val mockCharacteristicChange: BluetoothGattCharacteristic = mock()
    private val mockCharacteristicMicsTurnedOn: BluetoothGattCharacteristic = mock()
    private val mockCharacteristicMicsTurnedOff: BluetoothGattCharacteristic = mock()
    private val fakeMetricaReporter = FakeMetricaReporter()
    private val rcuConnectionObservable = RcuConnectionObservable(mockRcuManager, fakeMetricaReporter)
    private val mockHandler: Handler = mock()
    private var characteristicValue: ByteArray = byteArrayOf()
    private val fakeDecoder = FakeDecoder()
    private val rcuVoiceServer: RcuVoiceServer
    private val header = byteArrayOf(0, 0, RcuMicsCommands.IMA_ADPCM_COMPRESSION, 0, 0, 0)

    init {
        rcuVoiceServer =
            RcuVoiceServer(
                mockRcuManager,
                mockServer,
                fakeDecoder,
                mockRcuUpdateManager,
                fakeMetricaReporter,
                mockHandler,
                rcuConnectionObservable
            )
    }

    private fun checkVoiceData(message: QuasarMessage, expectedValue: ByteArray, tag: Int) {
        assertTrue(message.hasRcuVoiceEvent())
        assertTrue(message.rcuVoiceEvent.hasTag())
        assertEquals(tag, message.rcuVoiceEvent.tag)
        assertTrue(message.rcuVoiceEvent.hasVoiceData())
        val actualValue = message.rcuVoiceEvent.voiceData.toByteArray()
        assert(expectedValue.contentEquals(actualValue))
    }

    @Before
    fun setup() {
        whenever(mockCharacteristicChange.uuid).thenReturn(RcuMicsCommands.VOICE_DATA_CHARACTERISTIC_UUID)
        whenever(mockCharacteristicChange.value).thenAnswer { characteristicValue }

        whenever(mockCharacteristicMicsTurnedOn.uuid).thenReturn(RcuMicsCommands.MIC_CONTROL_CHARACTERISTIC)
        whenever(mockCharacteristicMicsTurnedOn.value).thenAnswer { RcuMicsCommands.startMicsCommand.value }

        whenever(mockCharacteristicMicsTurnedOff.uuid).thenReturn(RcuMicsCommands.MIC_CONTROL_CHARACTERISTIC)
        whenever(mockCharacteristicMicsTurnedOff.value).thenAnswer { RcuMicsCommands.stopMicsCommand.value }

        rcuConnectionObservable.receiveValue(RcuConnectionObservable.RcuConnectionInfo(mockBluetoothDevice, BluetoothGatt.STATE_CONNECTED))
    }

    @Test
    fun when_start_then_pauseAllUpdates() {
        val tag = 3
        rcuVoiceServer.start(tag)
        verify(mockRcuUpdateManager).pauseAllUpdates()
    }

    @Test
    fun when_gotStopEvent_then_resumeAllUpdates() {
        val tag = 3
        rcuVoiceServer.start(tag)
        // Mics turned on event
        rcuVoiceServer.onCharacteristicWrite(mockBluetoothDevice, mockCharacteristicMicsTurnedOn)
        rcuVoiceServer.stop(tag)
        // Mics turned off event
        rcuVoiceServer.onCharacteristicWrite(mockBluetoothDevice, mockCharacteristicMicsTurnedOff)


        verify(mockRcuUpdateManager).resumeAllUpdates()
    }

    @Test
    fun when_start_then_sendNothing() {
        val tag = 3
        rcuVoiceServer.start(tag)

        val rcuVoiceEvent =
            RcuVoiceEvent.newBuilder().setStartStreaming(EmptyMessage.newBuilder()).setTag(tag)
        val expectedMessage = QuasarMessage.newBuilder().setRcuVoiceEvent(rcuVoiceEvent)
        verify(mockServer, never()).sendToAll(expectedMessage.build())
    }

    @Test
    fun when_stop_then_sendNothing() {
        val tag = 3
        rcuVoiceServer.start(tag)
        // Mics turned on event
        rcuVoiceServer.onCharacteristicWrite(mockBluetoothDevice, mockCharacteristicMicsTurnedOn)
        rcuVoiceServer.stop(tag)

        val rcuVoiceEvent =
            RcuVoiceEvent.newBuilder().setStopStreaming(EmptyMessage.newBuilder()).setTag(tag)
        val expectedMessage = QuasarMessage.newBuilder().setRcuVoiceEvent(rcuVoiceEvent)
        verify(mockServer, never()).sendToAll(expectedMessage.build())
    }

    @Test
    fun when_gotStartEvent_then_sendStartEvent() {
        val tag = 3
        rcuVoiceServer.start(tag)
        // Mics turned on event
        rcuVoiceServer.onCharacteristicWrite(mockBluetoothDevice, mockCharacteristicMicsTurnedOn)

        val rcuVoiceEvent =
            RcuVoiceEvent.newBuilder().setStartStreaming(EmptyMessage.newBuilder()).setTag(tag)
        val expectedMessage = QuasarMessage.newBuilder().setRcuVoiceEvent(rcuVoiceEvent)
        verify(mockServer).sendToAll(expectedMessage.build())
        assertTrue(fakeDecoder.isStateCleared)
    }

    @Test
    fun when_gotStopEvent_then_sendStopEvent() {
        val tag = 3
        rcuVoiceServer.start(tag)
        // Mics turned on event
        rcuVoiceServer.onCharacteristicWrite(mockBluetoothDevice, mockCharacteristicMicsTurnedOn)
        rcuVoiceServer.stop(tag)
        // Mics turned off event
        rcuVoiceServer.onCharacteristicWrite(mockBluetoothDevice, mockCharacteristicMicsTurnedOff)

        val rcuVoiceEvent =
            RcuVoiceEvent.newBuilder().setStopStreaming(EmptyMessage.newBuilder()).setTag(tag)
        val expectedMessage = QuasarMessage.newBuilder().setRcuVoiceEvent(rcuVoiceEvent)
        verify(mockServer).sendToAll(expectedMessage.build())
    }

    @Test
    fun when_startAndStopSeveralTimes_thenProcessEventsInTheOrder() {
        for (i in 1..7) {
            rcuVoiceServer.start(i)
            rcuVoiceServer.stop(i)
        }

        for (i in 1..7) {
            // Mics turned on event
            rcuVoiceServer.onCharacteristicWrite(mockBluetoothDevice, mockCharacteristicMicsTurnedOn)
            val startStreaming =
                RcuVoiceEvent.newBuilder().setStartStreaming(EmptyMessage.newBuilder()).setTag(i)
            val expectedMessageStart = QuasarMessage.newBuilder().setRcuVoiceEvent(startStreaming)
            verify(mockServer).sendToAll(expectedMessageStart.build())

            // Mics turned off event
            rcuVoiceServer.onCharacteristicWrite(mockBluetoothDevice, mockCharacteristicMicsTurnedOff)
            val stopStreaming =
                RcuVoiceEvent.newBuilder().setStopStreaming(EmptyMessage.newBuilder()).setTag(i)
            val expectedMessageStop = QuasarMessage.newBuilder().setRcuVoiceEvent(stopStreaming)
            verify(mockServer).sendToAll(expectedMessageStop.build())
        }
    }

    @Test
    fun when_characteristicChanged_then_decodeAndSendDataToClient() {
        val tag = 3
        rcuVoiceServer.start(tag)
        // Mics turned on event
        rcuVoiceServer.onCharacteristicWrite(mockBluetoothDevice, mockCharacteristicMicsTurnedOn)

        for (i in 1..100) {
            clearInvocations(mockServer)
            characteristicValue = byteArrayOf(*header, i.toByte())

            rcuVoiceServer.onCharacteristicChanged(mockBluetoothDevice, mockCharacteristicChange)

            val expectedArray = byteArrayOf(i.toByte(), i.toByte())
            argumentCaptor<QuasarMessage> {
                verify(mockServer).sendToAll(capture())
                val message = firstValue
                checkVoiceData(message, expectedArray, tag)
            }
        }
    }

    class FakeDecoder : ADPCMDecoder() {
        var isStateCleared = false

        override fun decodeBlock(data: ByteArray, headerSize: Int): ByteArray {
            // Double values to verify decode has been called
            val headerless = data.copyOfRange(headerSize, data.size)
            return byteArrayOf(*headerless, *headerless)
        }

        override fun clearState() {
            isStateCleared = true
        }
    }
}
