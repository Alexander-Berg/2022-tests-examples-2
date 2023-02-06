package ru.yandex.quasar.app.utils

import org.junit.Assert
import org.junit.Before
import org.junit.Test
import org.mockito.Mockito
import ru.yandex.quasar.TestUtils.genMock
import ru.yandex.quasar.app.utils.waiting.Bootstrap
import ru.yandex.quasar.core.utils.Observable

class BootstrapTest {

    private lateinit var observable: Observable<Int>

    private lateinit var bootstrap: Bootstrap<Int>

    private lateinit var onReadyListener: (Int) -> Unit

    @Before
    fun runBeforeEachTest() {
        observable =
            CurrentThreadObservable()
        bootstrap = Bootstrap(observable)
        onReadyListener = genMock()
    }

    @Test
    fun onReadyListener_shouldNotBeCalled_ifObservableHasNoValue() {
        bootstrap.whenReady(onReadyListener)

        Mockito.verify(onReadyListener, Mockito.never()).invoke(Mockito.anyInt())
    }

    @Test
    fun whenReadyMethod_shouldWaitValue_ifObservableHasNoValue() {
        bootstrap.whenReady(onReadyListener)
        observable.receiveValue(0)

        Mockito.verify(onReadyListener, Mockito.times(1)).invoke(0)
    }

    @Test
    fun whenReadyMethod_shouldNotifyListener_ifObservableHasValue() {
        observable.receiveValue(0)
        bootstrap.whenReady(onReadyListener)

        Mockito.verify(onReadyListener, Mockito.times(1)).invoke(0)
    }

    @Test
    fun onReadyListener_shouldNotBeCalledTwice_ifObservableHasNoValue() {
        bootstrap.whenReady(onReadyListener)
        observable.receiveValue(0)
        observable.receiveValue(1)

        Mockito.verify(onReadyListener, Mockito.never()).invoke(1)
    }

    @Test
    fun onReadyListener_shouldNotBeCalledTwice_ifObservableHasValue() {
        observable.receiveValue(0)
        bootstrap.whenReady(onReadyListener)
        observable.receiveValue(1)

        Mockito.verify(onReadyListener, Mockito.never()).invoke(1)
    }

    @Test
    fun onReadyListener_shouldBeCalledWithLatestValue_ifObservableWasUpdatedTwoTimes() {
        observable.receiveValue(0)
        observable.receiveValue(1)
        bootstrap.whenReady(onReadyListener)

        Mockito.verify(onReadyListener, Mockito.never()).invoke(0)
        Mockito.verify(onReadyListener, Mockito.times(1)).invoke(1)
    }

    @Test
    fun isReady_shouldReturnFalse_ifObservableHasNoValue() {
        Assert.assertFalse(bootstrap.isReady())
    }

    @Test
    fun isReady_shouldReturnTrue_ifObservableReceivedValue() {
        observable.receiveValue(0)
        Assert.assertTrue(bootstrap.isReady())
    }

    @Test
    fun isReady_shouldReturnFalse_ifObservableReceivedNull() {
        observable.receiveValue(null)
        Assert.assertFalse(bootstrap.isReady())
    }

    @Test
    fun isReady_shouldReturnTrue_ifObservableReceivedNullAfterSomeNonNullValue() {
        observable.receiveValue(0)
        observable.receiveValue(null)
        Assert.assertTrue(bootstrap.isReady())
    }

    @Test
    fun onReadyListener_shouldNotBeCalled_ifObservableReceivedNull() {
        bootstrap.whenReady(onReadyListener)
        observable.receiveValue(null)
        Mockito.verify(onReadyListener, Mockito.never()).invoke(Mockito.anyInt())
    }

    class CurrentThreadObservable<T> : Observable<T>() {
        private var currentValue: T? = null

        override fun getCurrent(): T? {
            return currentValue
        }

        override fun receiveValue(newT: T?) {
            currentValue = newT
            notifyObservers(currentValue)
        }
    }
}
