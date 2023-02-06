package ru.yandex.quasar.transport

import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.ArgumentMatchers.any
import org.mockito.ArgumentMatchers.anyBoolean
import org.mockito.ArgumentMatchers.anyLong
import org.mockito.Mockito.`when`
import org.mockito.Mockito.mock
import org.mockito.Mockito.never
import org.mockito.Mockito.verify
import java.util.UUID
import java.util.concurrent.Callable
import java.util.concurrent.ExecutionException
import java.util.concurrent.Executor
import java.util.concurrent.ScheduledExecutorService
import java.util.concurrent.ScheduledFuture
import java.util.concurrent.TimeUnit
import java.util.concurrent.TimeoutException

@RunWith(value = AndroidJUnit4::class)
class QuasarRequestFutureTest {

    @Test
    fun returnsResultOnSuccess() {
        val future = createFuture<Any>(mock(Executor::class.java))
        val result = Any()
        future.setSuccess(result)
        assertEquals(result, future.get())
    }

    @Test(expected = ExecutionException::class)
    fun getThrowsExceptionOnFailure() {
        val future = createFuture<Any>(mock(Executor::class.java))
        future.setFailure(RuntimeException())
        future.get()
    }

    @Test
    fun isDoneReturnsTrueOnSuccess() {
        val future = createFuture<Any>(mock(Executor::class.java))
        future.setSuccess(Any())
        assertTrue(future.isDone)
    }

    @Test
    fun isDoneReturnsTrueOnFailure() {
        val future = createFuture<Any>(mock(Executor::class.java))
        future.setFailure(RuntimeException())
        assertTrue(future.isDone)
    }

    @Test
    fun isDoneReturnsFalseWhenNothingIsSet() {
        val future = createFuture<Any>(mock(Executor::class.java))
        assertFalse(future.isDone)
    }

    @Test
    fun cancelCancelsFutureWhenNothingIsSet() {
        val future = createFuture<Any>(mock(Executor::class.java))
        assertTrue(future.cancel(true))
    }

    @Test
    fun cancelFailsToCancelFutureWhenResultIsSet() {
        val future = createFuture<Any>(mock(Executor::class.java))
        future.setSuccess(Any())
        assertFalse(future.cancel(true))
    }

    @Test
    fun cancelFailsToCancelFutureWhenFailureIsSet() {
        val future = createFuture<Any>(mock(Executor::class.java))
        future.setFailure(RuntimeException())
        assertFalse(future.cancel(true))
    }

    @Test
    fun isCancelledReturnsTrueWhenCancelled() {
        val future = createFuture<Any>(mock(Executor::class.java))
        future.cancel(true)
        assertTrue(future.isCancelled)
    }

    @Test
    fun isCancelledReturnsFalseWhenNotCancelled() {
        val future = createFuture<Any>(mock(Executor::class.java))
        assertFalse(future.isCancelled)
    }

    @Test
    fun addListenerExecutesListenerImmediatelyIfFutureIsDone() {
        val listener = mock(Runnable::class.java)
        val future = createFuture<Any>(Executor { command -> command!!.run() })
        future.setSuccess(Any())
        future.addListener(listener)
        verify(listener).run()
    }

    @Test
    fun addListenerSchedulesListenerWhenFutureIsNotDone() {
        val listener = mock(Runnable::class.java)
        val future = createFuture<Any>(Executor { command -> command!!.run() })
        future.addListener(listener)
        verify(listener, never()).run()
    }

    @Test
    fun futureFailsOnTimeout() {
        val future = createFuture<Any>(Executor { command -> command!!.run() })
        val executorService = mock(ScheduledExecutorService::class.java)
        `when`(executorService.schedule(any(Callable::class.java), anyLong(), any())).then {
            (it.arguments[0] as Callable<*>).call()
            return@then mock(ScheduledFuture::class.java)
        }
        future.setTimeout(executorService, 1, TimeUnit.SECONDS)
        assertTrue(future.isDone)
        try {
            future.get()
        } catch (ex: ExecutionException) {
            assertTrue(ex.cause is TimeoutException)
        }
    }

    @Test
    fun timeoutCancelsOnFutureIsDone() {
        val future = createFuture<Any>(Executor { command -> command!!.run() })
        val executorService = mock(ScheduledExecutorService::class.java)
        val scheduledFuture = mock(ScheduledFuture::class.java)
        `when`(executorService.schedule(any(Callable::class.java), anyLong(), any())).then {
            return@then scheduledFuture
        }
        future.setTimeout(executorService, 1, TimeUnit.SECONDS)
        future.setSuccess(Any())
        verify(scheduledFuture).cancel(anyBoolean())
    }

    @Test
    fun setTimeoutDoesNothingOnFutureIsDone() {
        val future = createFuture<Any>(Executor { command -> command!!.run() })
        val executorService = mock(ScheduledExecutorService::class.java)
        future.setSuccess(Any())
        future.setTimeout(executorService, 1, TimeUnit.SECONDS)
        verify(executorService, never()).schedule(any(Callable::class.java), anyLong(), any())
    }

    @Test
    fun setSuccessReturnsTrueAndNotifiesListenersIfFutureIsNotDone() {
        val listener = mock(Runnable::class.java)
        val future = createFuture<Any>(Executor { command -> command!!.run() })
        future.addListener(listener)
        assertTrue(future.setSuccess(Any()))
        verify(listener).run()
    }

    @Test
    fun setSuccessReturnsFalseAndDoNothingIfFutureIsFailed() {
        val listener = mock(Runnable::class.java)
        val future = createFuture<Any>(Executor { command -> command!!.run() })
        future.addListener(listener)
        future.setFailure(RuntimeException())
        assertFalse(future.setSuccess(Any()))
        verify(listener).run() //listener should be called once on setFailure
    }

    @Test
    fun setSuccessReturnsFalseAndDoNothingIfFutureIsSucceed() {
        val listener = mock(Runnable::class.java)
        val future = createFuture<Any>(Executor { command -> command!!.run() })
        future.addListener(listener)
        future.setSuccess(Any())
        assertFalse(future.setSuccess(Any()))
        verify(listener).run() //listener should be called once on first setSuccess call
    }

    @Test
    fun setFailureReturnsTrueAndNotifiesListenersIfFutureIsNotDone() {
        val listener = mock(Runnable::class.java)
        val future = createFuture<Any>(Executor { command -> command!!.run() })
        future.addListener(listener)
        assertTrue(future.setFailure(RuntimeException()))
        verify(listener).run()
    }

    @Test
    fun setFailureReturnsFalseAndDoNothingIfFutureIsFailed() {
        val listener = mock(Runnable::class.java)
        val future = createFuture<Any>(Executor { command -> command!!.run() })
        future.addListener(listener)
        future.setFailure(RuntimeException())
        assertFalse(future.setFailure(RuntimeException()))
        verify(listener).run() //listener should be called once on first setFailure call
    }

    @Test
    fun setFailureReturnsFalseAndDoNothingIfFutureIsSucceed() {
        val listener = mock(Runnable::class.java)
        val future = createFuture<Any>(Executor { command -> command!!.run() })
        future.addListener(listener)
        future.setSuccess(Any())
        assertFalse(future.setFailure(RuntimeException()))
        verify(listener).run() //listener should be called once on setSuccess call
    }

    private fun <T> createFuture(executor: Executor): QuasarRequestFuture<T> {
        return QuasarRequestFuture<T>(UUID.randomUUID().toString(), executor)
    }
}