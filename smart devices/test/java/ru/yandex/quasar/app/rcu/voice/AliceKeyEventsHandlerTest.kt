package ru.yandex.quasar.app.rcu.voice

import android.view.KeyEvent
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.any
import org.mockito.kotlin.clearInvocations
import org.mockito.kotlin.inOrder
import org.mockito.kotlin.mock
import org.mockito.kotlin.never
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import ru.yandex.quasar.app.configs.RcuConfig
import ru.yandex.quasar.app.configs.SystemConfig
import ru.yandex.quasar.app.rcu.sender.RcuCommandSender
import ru.yandex.quasar.app.rcu.sender.RcuManager
import ru.yandex.quasar.app.rcu.utils.RcuEventTagProvider
import ru.yandex.quasar.fakes.ExternalConfigObservableFake
import ru.yandex.quasar.fakes.FakeMetricaReporter
import ru.yandex.quasar.shadows.ShadowThreadUtil

@RunWith(RobolectricTestRunner::class)
@Config(
    shadows = [ShadowThreadUtil::class],
    instrumentedPackages = ["ru.yandex.quasar.concurrency"]
)
class AliceKeyEventsHandlerTest {
    private val mockRcuManager: RcuManager = mock()
    private val mockRcuCommandSender: RcuCommandSender = mock()
    private val mockRcuVoiceServer: RcuVoiceServer = mock()
    private val mockRcuEventTagProvider: RcuEventTagProvider = mock()
    private val fakeMetricaReporter = FakeMetricaReporter()
    private val fakeConfigObservable = ExternalConfigObservableFake()
    private val aliceKeyEventsHandler =
        AliceKeyEventsHandler(
            mockRcuManager,
            mockRcuVoiceServer,
            fakeMetricaReporter,
            mockRcuEventTagProvider,
            fakeConfigObservable
        )

    @Before
    fun setUp() {
        whenever(mockRcuManager.getActiveCommandSender()).thenReturn(mockRcuCommandSender)
        whenever(mockRcuCommandSender.isServiceExists(any())).thenReturn(true)
        setSingleClickActivationEnabled(false)
    }

    private fun setSingleClickActivationEnabled(singleClickActivationEnabled: Boolean) {
        val systemConfig: SystemConfig = mock()
        val rcuConfig: RcuConfig = mock()
        whenever(systemConfig.rcuConfig).thenReturn(rcuConfig)
        whenever(rcuConfig.singleClickActivationEnabled).thenReturn(singleClickActivationEnabled)
        whenever(rcuConfig.turnOnMicsDelayEnabled).thenReturn(true)
        fakeConfigObservable.receiveSystemConfig(systemConfig)
    }

    @Test
    fun given_noButtonPressed_when_isNotSearchButtonPressed_then_doNotHandle() {
        val code = KeyEvent.KEYCODE_VOLUME_UP
        val event = KeyEvent(KeyEvent.ACTION_DOWN, code)

        assertFalse(aliceKeyEventsHandler.onKeyDown(code, event, false))

        verify(mockRcuVoiceServer, never()).start(0)
        verify(mockRcuCommandSender, never()).send(any())
    }

    @Test
    fun given_buttonPressed_when_isNotSearchButtonReleased_then_doNotHandle() {
        val code = KeyEvent.KEYCODE_VOLUME_UP
        val eventUp = KeyEvent(KeyEvent.ACTION_UP, code)
        val eventDown = KeyEvent(KeyEvent.ACTION_DOWN, code)
        aliceKeyEventsHandler.onKeyDown(code, eventDown, false)

        assertFalse(aliceKeyEventsHandler.onKeyUp(code, eventUp, false))

        verify(mockRcuVoiceServer, never()).stop(0)
        verify(mockRcuCommandSender, never()).send(any())
    }

    @Test
    fun given_noButtonPressed_when_searchButtonPressed_then_startServerAndTurnOnMics() {
        val code = KeyEvent.KEYCODE_SEARCH
        val event = KeyEvent(KeyEvent.ACTION_DOWN, code)

        assertFalse(aliceKeyEventsHandler.onKeyDown(code, event, false))

        inOrder(mockRcuCommandSender, mockRcuVoiceServer) {
            verify(mockRcuVoiceServer).start(0)
            verify(mockRcuCommandSender).send(RcuMicsCommands.startMicsCommand)
        }
    }

    @Test
    fun given_searchButtonPressed_when_searchButtonReleased_then_turnOffMicsAndStopServer() {
        val code = KeyEvent.KEYCODE_SEARCH
        val eventUp = KeyEvent(KeyEvent.ACTION_UP, code)
        val eventDown = KeyEvent(KeyEvent.ACTION_DOWN, code)
        aliceKeyEventsHandler.onKeyDown(code, eventDown, false)

        assertFalse(aliceKeyEventsHandler.onKeyUp(code, eventUp, false))

        inOrder(mockRcuCommandSender, mockRcuVoiceServer) {
            verify(mockRcuCommandSender).send(RcuMicsCommands.stopMicsCommand)
            verify(mockRcuVoiceServer).stop(0)
        }
    }

    @Test
    fun given_serviceDoNotExists_when_searchButtonPressed_then_doNothing() {
        val code = KeyEvent.KEYCODE_SEARCH
        val event = KeyEvent(KeyEvent.ACTION_DOWN, code)
        whenever(mockRcuCommandSender.isServiceExists(any())).thenReturn(false)

        assertTrue(aliceKeyEventsHandler.onKeyDown(code, event, false))

        verify(mockRcuVoiceServer, never()).start(0)
        verify(mockRcuCommandSender, never()).send(RcuMicsCommands.startMicsCommand)
    }

    @Test
    fun given_serviceDoNotExists_when_searchButtonReleased_then_doNotStartServer() {
        val code = KeyEvent.KEYCODE_SEARCH
        val eventUp = KeyEvent(KeyEvent.ACTION_UP, code)
        val eventDown = KeyEvent(KeyEvent.ACTION_DOWN, code)
        whenever(mockRcuCommandSender.isServiceExists(any())).thenReturn(false)
        aliceKeyEventsHandler.onKeyDown(code, eventDown, false)

        assertFalse(aliceKeyEventsHandler.onKeyUp(code, eventUp, false))

        verify(mockRcuCommandSender, never()).send(RcuMicsCommands.stopMicsCommand)
        verify(mockRcuVoiceServer, never()).stop(0)
    }

    @Test
    fun given_serviceMissed_when_searchButtonReleased_then_serverStopped() {
        val code = KeyEvent.KEYCODE_SEARCH
        val eventUp = KeyEvent(KeyEvent.ACTION_UP, code)
        val eventDown = KeyEvent(KeyEvent.ACTION_DOWN, code)
        aliceKeyEventsHandler.onKeyDown(code, eventDown, false)

        // Miss server after pressing the button
        whenever(mockRcuCommandSender.isServiceExists(any())).thenReturn(false)
        assertFalse(aliceKeyEventsHandler.onKeyUp(code, eventUp, false))

        verify(mockRcuCommandSender, never()).send(RcuMicsCommands.stopMicsCommand)
        // Server has to be stopped anyway
        verify(mockRcuVoiceServer).stop(0)
    }

    @Test
    fun given_searchButtonIsNotPressed_when_searchButtonReleased_then_doNotHandle() {
        val code = KeyEvent.KEYCODE_SEARCH
        val event = KeyEvent(KeyEvent.ACTION_UP, code)

        assertFalse(aliceKeyEventsHandler.onKeyUp(code, event, false))

        verify(mockRcuCommandSender, never()).send(RcuMicsCommands.stopMicsCommand)
        verify(mockRcuVoiceServer, never()).stop(0)
    }

    @Test
    fun given_searchButtonIsPressed_when_searchButtonPressed_then_doNotHandle() {
        val code = KeyEvent.KEYCODE_SEARCH
        val event = KeyEvent(KeyEvent.ACTION_DOWN, code)
        aliceKeyEventsHandler.onKeyDown(code, event, false)
        clearInvocations(mockRcuVoiceServer)
        clearInvocations(mockRcuCommandSender)

        assertFalse(aliceKeyEventsHandler.onKeyDown(code, event, false))

        verify(mockRcuCommandSender, never()).send(RcuMicsCommands.startMicsCommand)
        verify(mockRcuVoiceServer, never()).stop(0)
    }

    @Test
    fun given_noButtonPressed_when_searchButtonPressed_then_sendEvent() {
        val code = KeyEvent.KEYCODE_SEARCH
        val event = KeyEvent(KeyEvent.ACTION_DOWN, code)

        assertFalse(aliceKeyEventsHandler.onKeyDown(code, event, false))

        assertEquals(1, fakeMetricaReporter.latencyPoints.size)
        assertEquals(1, fakeMetricaReporter.latencies.size)
        assertEquals(AliceKeyEventsHandler.TAG, fakeMetricaReporter.latencyPoints.first())
        assertEquals(AliceKeyEventsHandler.TAG, fakeMetricaReporter.latencies.first().pointName)
        assertEquals(
            AliceKeyEventsHandler.MICS_TURNED_ON,
            fakeMetricaReporter.latencies.first().eventName
        )
        assertFalse(fakeMetricaReporter.latencies.first().removePoint)
    }

    @Test
    fun given_searchButtonPressed_when_searchButtonReleased_then_sendEvent() {
        val code = KeyEvent.KEYCODE_SEARCH
        val eventUp = KeyEvent(KeyEvent.ACTION_UP, code)
        val eventDown = KeyEvent(KeyEvent.ACTION_DOWN, code)
        aliceKeyEventsHandler.onKeyDown(code, eventDown, false)
        fakeMetricaReporter.latencyPoints.clear()
        fakeMetricaReporter.latencies.clear()

        assertFalse(aliceKeyEventsHandler.onKeyUp(code, eventUp, false))

        assertEquals(0, fakeMetricaReporter.latencyPoints.size)
        assertEquals(1, fakeMetricaReporter.latencies.size)
        assertEquals(AliceKeyEventsHandler.TAG, fakeMetricaReporter.latencies.first().pointName)
        assertEquals(
            AliceKeyEventsHandler.MICS_TURNED_OFF,
            fakeMetricaReporter.latencies.first().eventName
        )
        assertTrue(fakeMetricaReporter.latencies.first().removePoint)
    }

    @Test
    fun given_singleClickEnabled_when_searchButtonPressedOnce_then_doNothing() {
        setSingleClickActivationEnabled(true)
        val code = KeyEvent.KEYCODE_SEARCH
        val event = KeyEvent(KeyEvent.ACTION_DOWN, code)

        assertFalse(aliceKeyEventsHandler.onKeyDown(code, event, false))

        verify(mockRcuVoiceServer, never()).start(0)
        verify(mockRcuCommandSender, never()).send(RcuMicsCommands.startMicsCommand)
    }

    @Test
    fun given_singleClickEnabled_when_searchButtonLongPressed_then_startServerAndTurnOnMics() {
        setSingleClickActivationEnabled(true)
        val code = KeyEvent.KEYCODE_SEARCH
        val event = KeyEvent(KeyEvent.ACTION_DOWN, code)

        assertFalse(aliceKeyEventsHandler.onKeyDown(code, event, true))

        inOrder(mockRcuCommandSender, mockRcuVoiceServer) {
            verify(mockRcuVoiceServer).start(0)
            verify(mockRcuCommandSender).send(RcuMicsCommands.startMicsCommand)
        }
    }
}
