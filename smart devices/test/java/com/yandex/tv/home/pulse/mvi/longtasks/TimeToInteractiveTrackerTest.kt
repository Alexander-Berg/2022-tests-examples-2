package com.yandex.tv.home.pulse.mvi.longtasks

import android.os.Looper
import android.os.SystemClock
import com.yandex.tv.home.EmptyTestApp
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.equalTo
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.LooperMode
import org.robolectric.shadow.api.Shadow
import org.robolectric.shadows.ShadowLooper
import org.robolectric.shadows.ShadowSystemClock
import java.time.Duration
import java.util.concurrent.TimeUnit
import kotlin.test.assertFalse

@RunWith(RobolectricTestRunner::class)
@Config(shadows = [ShadowSystemClock::class], application = EmptyTestApp::class)
class TimeToInteractiveTrackerTest {
    private val looper = Looper.myLooper()!!
    private var firstFrameDrawnTimestamp = 0L

    @Before
    fun setUp() {
        SystemClock.setCurrentTimeMillis(INITIAL_UPTIME_MILLIS)
        firstFrameDrawnTimestamp = SystemClock.elapsedRealtime()
    }

    @Test
    fun `time to interactive with single long task`() {
        var interactiveStart = -1L
        var totalBlockingTime = -1L
        val tracker = TimeToInteractiveTracker(looper, firstFrameDrawnTimestamp, MIN_INTERACTIVE_WINDOW) { start, tbt ->
            interactiveStart = start
            totalBlockingTime = tbt
        }

        val taskDuration = MIN_LONG_TASK_DURATION * 2
        tracker.simulateLongTask(taskDuration)
        idleFor(MIN_INTERACTIVE_WINDOW)

        assertThat(interactiveStart, equalTo(firstFrameDrawnTimestamp + taskDuration))
        assertThat(totalBlockingTime, equalTo(taskDuration))
    }

    @Test
    fun `time to interactive with several tasks`() {
        var interactiveStart = -1L
        var totalBlockingTime = -1L
        val tracker = TimeToInteractiveTracker(looper, firstFrameDrawnTimestamp, MIN_INTERACTIVE_WINDOW) { start, tbt ->
            interactiveStart = start
            totalBlockingTime = tbt
        }

        val tasksDurations = listOf(MIN_LONG_TASK_DURATION, MIN_LONG_TASK_DURATION * 3, MIN_LONG_TASK_DURATION * 2)
        val totalDuration = tasksDurations.sum()
        for (duration in tasksDurations) {
            tracker.simulateLongTask(duration)
        }
        idleFor(MIN_INTERACTIVE_WINDOW)

        assertThat(interactiveStart, equalTo(firstFrameDrawnTimestamp + totalDuration))
        assertThat(totalBlockingTime, equalTo(totalDuration))
    }

    @Test
    fun `time to interactive without long tasks`() {
        var interactiveStart = -1L
        var totalBlockingTime = -1L
        TimeToInteractiveTracker(looper, firstFrameDrawnTimestamp, MIN_INTERACTIVE_WINDOW) { start, tbt ->
            interactiveStart = start
            totalBlockingTime = tbt
        }

        idleFor(MIN_INTERACTIVE_WINDOW)

        assertThat(interactiveStart, equalTo(firstFrameDrawnTimestamp))
        assertThat(totalBlockingTime, equalTo(0))
    }

    @Test
    fun `callback is called only after min interactive window`() {
        var callbackCalled = false
        TimeToInteractiveTracker(looper, firstFrameDrawnTimestamp, MIN_INTERACTIVE_WINDOW) { _, _ ->
            callbackCalled = true
        }
        idleFor(MIN_INTERACTIVE_WINDOW / 2)
        assertFalse(callbackCalled)
        idleFor(MIN_INTERACTIVE_WINDOW / 2)
    }

    private fun LongTasksObserver.simulateLongTask(durationMs: Long) {
        val now = SystemClock.elapsedRealtime()
        ShadowSystemClock.advanceBy(Duration.ofMillis(durationMs))
        onLongTask(LongTask(TARGET, now, durationMs))
    }

    private fun idleFor(durationMs: Long) {
        val shadowLooper = Shadow.extract<ShadowLooper>(Looper.myLooper())
        shadowLooper.idleFor(durationMs, TimeUnit.MILLISECONDS)
    }

    companion object {
        private const val INITIAL_UPTIME_MILLIS = 1000L
        private const val MIN_LONG_TASK_DURATION = 50L
        private const val MIN_INTERACTIVE_WINDOW = 3000L
        private const val TARGET = "target"
    }
}
