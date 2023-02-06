package ru.yandex.quasar.app.rcu.buttons.navigation

import android.view.KeyEvent
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.mock
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import ru.yandex.quasar.app.configs.RcuConfig
import ru.yandex.quasar.app.configs.SystemConfig
import ru.yandex.quasar.app.services.MediaEventListener
import ru.yandex.quasar.fakes.ExternalConfigObservableFake
import ru.yandex.quasar.protobuf.ModelObjects.ControlRequest
import ru.yandex.quasar.shadows.ShadowThreadUtil

@RunWith(RobolectricTestRunner::class)
@Config(
    shadows = [ShadowThreadUtil::class],
    instrumentedPackages = ["ru.yandex.quasar.concurrency"]
)
class NavigationEventsHandlerTest {
    private class FakeMediaEventListener : MediaEventListener {
        var lastControlRequest: ControlRequest? = null

        override fun onControlRequest(controlRequest: ControlRequest): Boolean {
            lastControlRequest = controlRequest
            return true
        }
    }

    private val fakeConfigObservable = ExternalConfigObservableFake()
    private val fakeMediaEventListener = FakeMediaEventListener()
    private val navigationEventsHandler = NavigationEventsHandler(fakeConfigObservable)

    @Before
    fun setUp() {
        navigationEventsHandler.mediaEventListener = fakeMediaEventListener
    }

    private fun setNavigationEnabled(navigationEnabled: Boolean) {
        val systemConfig: SystemConfig = mock()
        val rcuConfig: RcuConfig = mock()
        whenever(systemConfig.rcuConfig).thenReturn(rcuConfig)
        whenever(rcuConfig.navigationEnabled).thenReturn(navigationEnabled)
        fakeConfigObservable.receiveSystemConfig(systemConfig)
    }

    private fun assertHandled(
        keyCode: Int,
        handledKeyDown: Boolean,
        handledKeyUp: Boolean
    ) {
        assertEquals(
            handledKeyDown,
            navigationEventsHandler.onKeyDown(
                keyCode,
                KeyEvent(KeyEvent.ACTION_DOWN, keyCode),
                false
            )
        )
        assertEquals(
            handledKeyDown,
            navigationEventsHandler.onKeyDown(
                keyCode,
                KeyEvent(KeyEvent.ACTION_DOWN, keyCode),
                true
            )
        )
        assertEquals(
            handledKeyUp,
            navigationEventsHandler.onKeyUp(keyCode, KeyEvent(KeyEvent.ACTION_UP, keyCode), false)
        )
        assertEquals(
            handledKeyUp,
            navigationEventsHandler.onKeyUp(keyCode, KeyEvent(KeyEvent.ACTION_UP, keyCode), true)
        )
    }

    @Test
    fun given_navigationEnabled_when_navigationButtonPressed_then_listenerGotEvent() {
        setNavigationEnabled(true)
        val keyCodes = listOf(
            KeyEvent.KEYCODE_DPAD_LEFT,
            KeyEvent.KEYCODE_DPAD_RIGHT,
            KeyEvent.KEYCODE_DPAD_DOWN,
            KeyEvent.KEYCODE_DPAD_UP
        )

        for (code in keyCodes) {
            navigationEventsHandler.onKeyDown(code, KeyEvent(KeyEvent.ACTION_DOWN, code), false)
            assertNotNull(fakeMediaEventListener.lastControlRequest)
            fakeMediaEventListener.lastControlRequest = null
        }
    }

    @Test
    fun given_navigationEnabled_when_actionButtonReleased_then_listenerGotEvent() {
        setNavigationEnabled(true)

        navigationEventsHandler.onKeyUp(
            KeyEvent.KEYCODE_DPAD_CENTER,
            KeyEvent(KeyEvent.ACTION_UP, KeyEvent.KEYCODE_DPAD_CENTER),
            false
        )
        assertNotNull(fakeMediaEventListener.lastControlRequest)
        fakeMediaEventListener.lastControlRequest = null
    }

    @Test
    fun given_navigationEnabled_when_actionButtonPressed_then_listenerGotNoEvents() {
        setNavigationEnabled(true)

        navigationEventsHandler.onKeyDown(
            KeyEvent.KEYCODE_DPAD_CENTER,
            KeyEvent(KeyEvent.ACTION_DOWN, KeyEvent.KEYCODE_DPAD_CENTER),
            false
        )
        assertNull(fakeMediaEventListener.lastControlRequest)
    }

    @Test
    fun given_navigationDisabled_when_navigationButtonPressed_then_listenerGotNoEvents() {
        setNavigationEnabled(false)
        val keyCodes = listOf(
            KeyEvent.KEYCODE_DPAD_CENTER,
            KeyEvent.KEYCODE_DPAD_LEFT,
            KeyEvent.KEYCODE_DPAD_RIGHT,
            KeyEvent.KEYCODE_DPAD_DOWN,
            KeyEvent.KEYCODE_DPAD_UP
        )

        for (code in keyCodes) {
            navigationEventsHandler.onKeyDown(code, KeyEvent(KeyEvent.ACTION_DOWN, code), false)
            assertNull(fakeMediaEventListener.lastControlRequest)
        }
    }

    @Test
    fun given_navigationEnabled_when_navigationButtonPressed_then_eventIsHandled() {
        setNavigationEnabled(true)
        val keyCodes = listOf(
            KeyEvent.KEYCODE_DPAD_LEFT,
            KeyEvent.KEYCODE_DPAD_RIGHT,
            KeyEvent.KEYCODE_DPAD_DOWN,
            KeyEvent.KEYCODE_DPAD_UP
        )

        for (code in keyCodes) {
            assertHandled(code, handledKeyDown = true, handledKeyUp = false)
        }
    }

    @Test
    fun given_navigationDisabled_when_navigationButtonPressed_then_eventIsNotHandled() {
        setNavigationEnabled(false)
        val keyCodes = listOf(
            KeyEvent.KEYCODE_DPAD_CENTER,
            KeyEvent.KEYCODE_DPAD_LEFT,
            KeyEvent.KEYCODE_DPAD_RIGHT,
            KeyEvent.KEYCODE_DPAD_DOWN,
            KeyEvent.KEYCODE_DPAD_UP
        )

        for (code in keyCodes) {
            assertHandled(code, handledKeyDown = false, handledKeyUp = false)
        }
    }

    @Test
    fun given_navigationEnabled_when_someButtonPressed_then_eventIsNotHandled() {
        setNavigationEnabled(true)
        val keyCodes = listOf(
            KeyEvent.KEYCODE_A,
            KeyEvent.KEYCODE_HOME,
            KeyEvent.KEYCODE_CAPS_LOCK,
            KeyEvent.KEYCODE_SYSTEM_NAVIGATION_LEFT,
            KeyEvent.KEYCODE_ENTER
        )

        for (code in keyCodes) {
            assertHandled(code, handledKeyDown = false, handledKeyUp = false)
        }
    }
}
