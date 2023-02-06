package ru.yandex.quasar.app.utils.waiting

import androidx.annotation.IntDef
import androidx.core.util.Consumer
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.ArgumentMatchers.anyInt
import org.mockito.kotlin.mock
import org.mockito.kotlin.never
import org.mockito.kotlin.verify
import ru.yandex.quasar.core.utils.Observable

@RunWith(AndroidJUnit4::class)
class ConditionWaitingTest {

    @Test
    fun when_observableHasNullCurrent_then_callbackIsNotCalled() {
        val waiting = createConditionWaiting(createObservable(ObservableValueType.NULL))
        val consumer = mock<Consumer<Int>>()
        assertNotNull(waiting.whenReady(consumer))
        verify(consumer, never()).accept(anyInt())
    }

    @Test
    fun when_observableHasInappropriateValue_then_callbackIsNotCalled() {
        val waiting = createConditionWaiting(createObservable(ObservableValueType.INAPPROPRIATE))
        val consumer = mock<Consumer<Int>>()
        assertNotNull(waiting.whenReady(consumer))
        verify(consumer, never()).accept(anyInt())
    }

    @Test
    fun when_observableHasAppropriateValue_then_callbackIsCalled() {
        val waiting = createConditionWaiting(createObservable(ObservableValueType.APPROPRIATE))
        val consumer = mock<Consumer<Int>>()
        assertNull(waiting.whenReady(consumer))
        verify(consumer).accept(ObservableValueType.APPROPRIATE)
    }

    @Test
    fun when_observableReceivesAppropriateValue_then_callbackIsCalled() {
        val observable = createObservable(ObservableValueType.NULL)
        val waiting = createConditionWaiting(observable)
        val consumer = mock<Consumer<Int>>()
        waiting.whenReady(consumer)
        observable.receiveValue(ObservableValueType.APPROPRIATE)
        verify(consumer).accept(ObservableValueType.APPROPRIATE)
    }

    @Test
    fun when_observableReceivesMultipleValues_then_callbackIsCalledOnce() {
        val observable = createObservable(ObservableValueType.NULL)
        val waiting = createConditionWaiting(observable)
        val consumer = mock<Consumer<Int>>()
        waiting.whenReady(consumer)
        observable.receiveValue(ObservableValueType.APPROPRIATE)
        observable.receiveValue(ObservableValueType.APPROPRIATE)
        verify(consumer).accept(ObservableValueType.APPROPRIATE)
    }

    @Test
    fun when_observerReceivesInappropriateValue_then_callbackIsNotCalled() {
        val observable = createObservable(ObservableValueType.NULL)
        val waiting = createConditionWaiting(observable)
        val consumer = mock<Consumer<Int>>()
        waiting.whenReady(consumer)
        observable.receiveValue(ObservableValueType.INAPPROPRIATE)
        verify(consumer, never()).accept(ObservableValueType.APPROPRIATE)
    }

    @Test
    fun when_observableReceivesAppropriateValue_then_disposableReturnsFalseOnDispose() {
        val observable = createObservable(ObservableValueType.NULL)
        val waiting = createConditionWaiting(observable)
        val consumer = mock<Consumer<Int>>()
        val disposable = waiting.whenReady(consumer)
        observable.receiveValue(ObservableValueType.APPROPRIATE)
        assertFalse(disposable!!.dispose())
    }

    @Test
    fun when_disposableDisposed_then_callbackIsNotCalled() {
        val observable = createObservable(ObservableValueType.NULL)
        val waiting = createConditionWaiting(observable)
        val consumer = mock<Consumer<Int>>()
        val disposable = waiting.whenReady(consumer)
        disposable!!.dispose()
        observable.receiveValue(ObservableValueType.APPROPRIATE)
        verify(consumer, never()).accept(ObservableValueType.APPROPRIATE)
    }

    private fun createObservable(@ObservableValueType value: Int): Observable<Int?> {
        val observable = Observable<Int?> {}
        observable.receiveValue(
            when(value) {
                ObservableValueType.NULL -> null
                else -> value
            }
        )
        return observable
    }

    private fun createConditionWaiting(observable: Observable<Int?>): ConditionWaiting<Int> {
        return ConditionWaiting(observable) { it == ObservableValueType.APPROPRIATE }
    }

    @IntDef(
        ObservableValueType.NULL,
        ObservableValueType.APPROPRIATE,
        ObservableValueType.INAPPROPRIATE
    )
    private annotation class ObservableValueType {
        companion object {
            const val NULL = 0
            const val APPROPRIATE = 1
            const val INAPPROPRIATE = 2
        }
    }
}
