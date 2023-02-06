package com.yandex.tv.home.pulse.mvi.firstinput

import android.os.SystemClock
import android.view.Choreographer
import android.view.KeyEvent
import com.yandex.tv.home.EmptyTestApp
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.equalTo
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.argumentCaptor
import org.mockito.kotlin.mock
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.Implementation
import org.robolectric.annotation.Implements
import org.robolectric.shadows.ShadowSystemClock
import java.time.Duration
import kotlin.test.assertFalse

@RunWith(RobolectricTestRunner::class)
@Config(
    application = EmptyTestApp::class,
    shadows = [ShadowSystemClock::class, FirstInputTrackerTest.ShadowChoreographer::class]
)
class FirstInputTrackerTest {
    @Before
    fun setUp() {
        val choreographer: Choreographer = mock()
        ShadowChoreographer.instance = choreographer

        val frameCallbackCaptor = argumentCaptor<Choreographer.FrameCallback>()
        whenever(choreographer.postFrameCallback(frameCallbackCaptor.capture())).then {
            ShadowSystemClock.advanceBy(Duration.ofMillis(FIRST_INPUT_PROCESS_DELAY))
            frameCallbackCaptor.firstValue.doFrame(System.nanoTime())
        }
    }

    @Test
    fun `callback on first button press`() {
        var firstInputDelay = -1L
        val firstInputTracker = FirstInputTracker { delay -> firstInputDelay = delay }
        firstInputTracker.simulateButtonPress(KeyEvent.KEYCODE_DPAD_DOWN)
        assertThat(firstInputDelay, equalTo(FIRST_INPUT_PROCESS_DELAY))
    }

    @Test
    fun `no callback on second button press`() {
        var callbackCalledCount = 0
        val firstInputTracker = FirstInputTracker { callbackCalledCount++ }
        firstInputTracker.simulateButtonPress(KeyEvent.KEYCODE_DPAD_CENTER)
        assertThat(callbackCalledCount, equalTo(1))
        firstInputTracker.simulateButtonPress(KeyEvent.KEYCODE_DPAD_DOWN)
        assertThat(callbackCalledCount, equalTo(1))
    }

    @Test
    fun `no callback on double action down`() {
        var callbackCalled = false
        val firstInputTracker = FirstInputTracker { callbackCalled = true }
        firstInputTracker.simulateEvent(KeyEvent.ACTION_DOWN, KeyEvent.KEYCODE_DPAD_UP)
        firstInputTracker.simulateEvent(KeyEvent.ACTION_DOWN, KeyEvent.KEYCODE_DPAD_UP)
        assertFalse(callbackCalled)
    }

    private fun FirstInputTracker.simulateEvent(action: Int, keyCode: Int) {
        val now = SystemClock.elapsedRealtime()
        val event = KeyEvent(now, now, action, keyCode, 1)
        onKeyEvent(event)
    }

    private fun FirstInputTracker.simulateButtonPress(keyCode: Int) {
        simulateEvent(KeyEvent.ACTION_DOWN, keyCode)
        ShadowSystemClock.advanceBy(Duration.ofMillis(FIRST_INPUT_START_DELAY))
        simulateEvent(KeyEvent.ACTION_UP, keyCode)
    }

    @Implements(Choreographer::class)
    internal object ShadowChoreographer {
        @get:Implementation
        @JvmStatic
        var instance: Choreographer? = null
    }

    companion object {
        private const val FIRST_INPUT_START_DELAY = 200L
        private const val FIRST_INPUT_PROCESS_DELAY = 150L
    }
}
