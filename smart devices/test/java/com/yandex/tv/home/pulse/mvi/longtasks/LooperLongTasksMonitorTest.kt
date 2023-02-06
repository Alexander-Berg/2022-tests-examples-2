package com.yandex.tv.home.pulse.mvi.longtasks

import android.os.Handler
import android.os.Looper
import android.os.Message
import android.os.SystemClock
import android.util.Printer
import com.yandex.tv.home.EmptyTestApp
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.equalTo
import org.junit.After
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.argumentCaptor
import org.mockito.kotlin.mock
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.shadows.ShadowSystemClock
import java.time.Duration
import kotlin.random.Random

@RunWith(RobolectricTestRunner::class)
@Config(application = EmptyTestApp::class, shadows = [ShadowSystemClock::class])
class LooperLongTasksMonitorTest {
    private val looper: Looper = mock()
    private val handler = Handler(looper)
    private val longTasksMonitor = LooperLongTasksMonitor(looper, MIN_LONG_TASK_DURATION)

    private var printer: Printer? = null

    @Before
    fun setUp() {
        val printerCaptor = argumentCaptor<Printer>()
        whenever(looper.setMessageLogging(printerCaptor.capture())).then {
            printer = printerCaptor.firstValue
            null
        }
    }

    @After
    fun clear() {
        longTasksMonitor.stop()
    }

    @Test
    fun `tasks with duration more than MIN_LONG_TASK_DURATION are treated as long tasks`() {
        var longTasks = 0
        longTasksMonitor.start { longTasks++ }
        val longTasksDurations = listOf(
            MIN_LONG_TASK_DURATION,
            MIN_LONG_TASK_DURATION + 1,
            2 * MIN_LONG_TASK_DURATION,
            Random.nextLong(MIN_LONG_TASK_DURATION, Long.MAX_VALUE)
        )
        for (duration in longTasksDurations) {
            dispatchMessage(createTaskWithDuration(duration))
        }
        assertThat(longTasks, equalTo(longTasksDurations.size))
    }

    @Test
    fun `tasks with duration less than MIN_LONG_TASK_DURATION are not treated as long tasks`() {
        var longTasks = 0
        longTasksMonitor.start { longTasks++ }
        val shortTasksDurations = listOf(
            0,
            MIN_LONG_TASK_DURATION - 1,
            MIN_LONG_TASK_DURATION / 2,
            Random.nextLong(0, MIN_LONG_TASK_DURATION)
        )
        for (duration in shortTasksDurations) {
            dispatchMessage(createTaskWithDuration(duration))
        }
        assertThat(longTasks, equalTo(0))
    }

    @Test
    fun `verify long task info`() {
        var longTask: LongTask? = null
        longTasksMonitor.start { longTask = it }

        val startTimeMs = SystemClock.elapsedRealtime()
        val duration = Random.nextLong(MIN_LONG_TASK_DURATION, Long.MAX_VALUE)
        dispatchMessage(createTaskWithDuration(duration))

        assertThat(longTask, equalTo(LongTask(TARGET, startTimeMs, duration)))
    }

    @Test
    fun `no long tasks received before start`() {
        var longTasks = 0
        dispatchMessage(createTaskWithDuration(MIN_LONG_TASK_DURATION))
        longTasksMonitor.start { longTasks++ }
        longTasksMonitor.stop()
        assertThat(longTasks, equalTo(0))
    }

    @Test
    fun `no long tasks received after stop`() {
        var longTasks = 0
        longTasksMonitor.start { longTasks++ }
        longTasksMonitor.stop()
        dispatchMessage(createTaskWithDuration(MIN_LONG_TASK_DURATION))
        assertThat(longTasks, equalTo(0))
    }

    private fun createTaskWithDuration(duration: Long): Message {
        return Message.obtain(handler) { ShadowSystemClock.advanceBy(Duration.ofMillis(duration)) }
    }

    private fun dispatchMessage(msg: Message) {
        // Robolectric shadow loopers do not use message logging as it is used
        // in platform looper implementation, so we manually simulate behavior
        // of real loop iteration. See original source:
        // https://android.googlesource.com/platform/frameworks/base/+/master/core/java/android/os/Looper.java
        val localPrinter = printer ?: return
        localPrinter.println(">>>>> Dispatching to $TARGET")
        msg.target.dispatchMessage(msg)
        localPrinter.println("<<<<< Finished to $TARGET")
    }

    companion object {
        private const val MIN_LONG_TASK_DURATION = 50L
        private const val TARGET = "target"
    }
}
