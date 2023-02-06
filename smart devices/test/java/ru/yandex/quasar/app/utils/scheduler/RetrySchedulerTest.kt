package ru.yandex.quasar.app.utils.scheduler

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.ArgumentMatchers.any
import org.mockito.ArgumentMatchers.anyLong
import org.mockito.Mockito.mock
import org.mockito.Mockito.never
import org.mockito.Mockito.verify
import org.mockito.kotlin.argumentCaptor
import org.mockito.kotlin.eq
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import java.util.concurrent.ScheduledExecutorService
import java.util.concurrent.ScheduledFuture
import java.util.concurrent.TimeUnit

@RunWith(RobolectricTestRunner::class)
class RetrySchedulerTest {

    @Test
    fun scheduleTimeSchedulerSchedulesTask() {
        val executorService = mock(ScheduledExecutorService::class.java)
        val retryScheduler = RetryScheduler(
            executorService,
            10000L,
            500L
        )
        retryScheduler.schedule { }
        assertTrue(retryScheduler.shouldRetry())
        verify(executorService).schedule(any(Runnable::class.java), anyLong(), any())
    }

    @Test
    fun scheduleTimeSchedulerIncreasesTimeout() {
        val executorService = mock(ScheduledExecutorService::class.java)
        val retryScheduler = RetryScheduler(
            executorService,
            500L,
            500L
        )
        retryScheduler.schedule { }
        assertFalse(retryScheduler.shouldRetry())
        verify(executorService).schedule(any(Runnable::class.java), anyLong(), any())
    }

    @Test
    fun cancelTimeSchedulerDisablesScheduler() {
        val executorService = mock(ScheduledExecutorService::class.java)
        whenever(executorService.schedule(any(Runnable::class.java), anyLong(), any()))
            .then {
                return@then mock(ScheduledFuture::class.java)
            }
        val retryScheduler = RetryScheduler(
            executorService,
            10000L,
            500L
        )
        retryScheduler.cancel()
        retryScheduler.schedule { }
        assertFalse(retryScheduler.shouldRetry())
        verify(executorService, never()).schedule(any(Runnable::class.java), anyLong(), any())
    }

    @Test
    fun scheduleAttemptsSchedulerSchedulesTask() {
        val executorService = mock(ScheduledExecutorService::class.java)
        val retryScheduler = AttemptsRetryScheduler(
            executorService,
            10000L,
            64000L,
            3
        )
        retryScheduler.schedule { }
        assertTrue(retryScheduler.shouldRetry())
        verify(executorService).schedule(any(Runnable::class.java), anyLong(), any())
    }

    @Test
    fun scheduleAttemptsSchedulerIncreasesAttempts() {
        val executorService = mock(ScheduledExecutorService::class.java)
        val retryScheduler = AttemptsRetryScheduler(
            executorService,
            500L,
            64000L,
            1
        )
        retryScheduler.schedule { }
        assertFalse(retryScheduler.shouldRetry())
        verify(executorService).schedule(any(Runnable::class.java), anyLong(), any())
    }

    @Test
    fun cancelAttemptsSchedulerDisablesScheduler() {
        val executorService = mock(ScheduledExecutorService::class.java)
        whenever(executorService.schedule(any(Runnable::class.java), anyLong(), any()))
            .then {
                return@then mock(ScheduledFuture::class.java)
            }
        val retryScheduler = AttemptsRetryScheduler(
            executorService,
            10000L,
            64000L,
            3
        )
        retryScheduler.cancel()
        retryScheduler.schedule { }
        assertFalse(retryScheduler.shouldRetry())
        verify(executorService, never()).schedule(any(Runnable::class.java), anyLong(), any())
    }

    @Test
    fun withRetryBackoffTimeIsLimitedByMaxBackoff() {
        val backoffTime = Array(1) { 0L }
        val executorService = mock(ScheduledExecutorService::class.java)
        whenever(executorService.schedule(any(Runnable::class.java), anyLong(), any()))
            .then {
                backoffTime[0] = (it.arguments[1] as Long)
                (it.arguments[0] as Runnable).run()
                return@then mock(ScheduledFuture::class.java)
            }
        whenever(executorService.submit(any(Runnable::class.java)))
            .then {
                (it.arguments[0] as Runnable).run()
                return@then mock(ScheduledFuture::class.java)
            }
        SchedulerTask.withRetry { throw RuntimeException() }
            .retries(10)
            .initRetryDelay(15_000)
            .onFinish {}
            .onFail {}
            .runOn(executorService)
        assertTrue(
            backoffTime[0] <= RetryScheduler.MAX_RANDOM_NUMBER_OF_MS + SchedulerTask.DEFAULT_MAX_BACKOFF_TIMEOUT_MS
                && backoffTime[0] >= SchedulerTask.DEFAULT_MAX_BACKOFF_TIMEOUT_MS)
    }

    @Test
    fun withRetryWithoutJitterExecutesImmediately() {
        val executorService = mock(ScheduledExecutorService::class.java)
        whenever(executorService.schedule(any(Runnable::class.java), anyLong(), any()))
            .then {
                return@then mock(ScheduledFuture::class.java)
            }
        // Run without jitter
        SchedulerTask.withRetry { throw RuntimeException() }
            .retries(1)
            .initRetryDelay(100)
            .onFinish {}
            .onFail {}
            .runOn(executorService)
        verify(executorService).schedule(any(Runnable::class.java), eq(0), any())
    }

    @Test
    fun withRetryFirstDelayIsLimitedByJitter() {
        val executorService = mock(ScheduledExecutorService::class.java)
        whenever(executorService.schedule(any(Runnable::class.java), anyLong(), any()))
            .then {
                return@then mock(ScheduledFuture::class.java)
            }
        // Run with jitter
        val minJitter = 3L
        val maxJitter = 5L
        val timeUnit = TimeUnit.SECONDS
        SchedulerTask.withRetry { throw RuntimeException() }
            .retries(1)
            .initRetryDelay(100)
            .jitter(minJitter, maxJitter, timeUnit)
            .onFinish {}
            .onFail {}
            .runOn(executorService)
        argumentCaptor<Long> {
            verify(executorService).schedule(any(Runnable::class.java), capture(), eq(TimeUnit.MILLISECONDS))
            val delay = firstValue
            assertTrue(delay >= timeUnit.toMillis(minJitter) && delay <= timeUnit.toMillis(maxJitter))
        }
    }
}
