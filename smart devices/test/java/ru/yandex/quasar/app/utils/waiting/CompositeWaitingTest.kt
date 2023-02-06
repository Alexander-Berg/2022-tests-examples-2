package ru.yandex.quasar.app.utils.waiting

import androidx.core.util.Consumer
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito.mock
import org.mockito.kotlin.anyOrNull
import org.mockito.kotlin.never
import org.mockito.kotlin.verify
import ru.yandex.quasar.core.utils.Disposable

@RunWith(AndroidJUnit4::class)
class CompositeWaitingTest {

    @Test
    fun when_everyWaitingIsReady_then_onReadyIsCalled() {
        val compositeWaiting = CompositeWaiting(
            SimpleWaiting(true),
            SimpleWaiting(true),
            SimpleWaiting(true)
        )
        val consumer = mock(Consumer::class.java) as Consumer<Any?>
        assertNull(compositeWaiting.whenReady(consumer))
        verify(consumer).accept(anyOrNull())
    }

    @Test
    fun when_atLeastOneWaitingIsNotReady_then_onReadyIsNotCalled() {
        val compositeWaiting = CompositeWaiting(
            SimpleWaiting(true),
            SimpleWaiting(false),
            SimpleWaiting(true)
        )
        val consumer = mock(Consumer::class.java) as Consumer<Any?>
        assertNotNull(compositeWaiting.whenReady(consumer))
        verify(consumer, never()).accept(anyOrNull())
    }

    @Test
    fun when_everyWaitingBecomesReady_then_onReadyIsCalled() {
        val notReadyWaiting = SimpleWaiting(false)
        val compositeWaiting = CompositeWaiting(
            SimpleWaiting(true),
            notReadyWaiting,
            SimpleWaiting(true)
        )
        val consumer = mock(Consumer::class.java) as Consumer<Any?>
        compositeWaiting.whenReady(consumer)
        notReadyWaiting.ready = true
        verify(consumer).accept(anyOrNull())
    }

    @Test
    fun when_everyEveryWaitingBecomesReady_then_disposableReturnsFalseOnDispose() {
        val notReadyWaiting = SimpleWaiting(false)
        val compositeWaiting = CompositeWaiting(
            SimpleWaiting(true),
            notReadyWaiting,
            SimpleWaiting(true)
        )
        val consumer = mock(Consumer::class.java) as Consumer<Any?>
        val disposable = compositeWaiting.whenReady(consumer)
        notReadyWaiting.ready = true
        assertFalse(disposable!!.dispose())
    }

    @Test
    fun when_disposableDisposed_then_callbackIsNotCalled() {
        val notReadyWaiting = SimpleWaiting(false)
        val compositeWaiting = CompositeWaiting(
            SimpleWaiting(true),
            notReadyWaiting,
            SimpleWaiting(true)
        )
        val consumer = mock(Consumer::class.java) as Consumer<Any?>
        val disposable = compositeWaiting.whenReady(consumer)
        val disposeResult = disposable!!.dispose()
        notReadyWaiting.ready = true
        assertTrue(disposeResult)
        verify(consumer, never()).accept(anyOrNull())
    }

    private class SimpleWaiting(ready: Boolean) : Waiting<Any> {

        private var onReady: ((Any) -> Unit)? = null

        var ready: Boolean = ready
            set(value) {
                field = value
                onReady?.invoke(Any())
                onReady = null
            }

        override fun whenReady(onReady: (Any) -> Unit): Disposable? {
            if (ready) {
                onReady(Any())
                return null
            }
            this.onReady = onReady
            return object : Disposable {
                override fun dispose(): Boolean {
                    if (this@SimpleWaiting.onReady == null) {
                        return false
                    }
                    this@SimpleWaiting.onReady = null
                    return true
                }
            }
        }
    }
}
