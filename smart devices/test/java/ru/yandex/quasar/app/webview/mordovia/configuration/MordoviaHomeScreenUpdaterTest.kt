package ru.yandex.quasar.app.webview.mordovia.configuration

import org.junit.Assert
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.any
import org.mockito.kotlin.mock
import org.mockito.kotlin.never
import org.mockito.kotlin.reset
import org.mockito.kotlin.times
import org.mockito.kotlin.verify
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import ru.yandex.quasar.app.webview.MordoviaConfiguration
import ru.yandex.quasar.fakes.FakeMetricaReporter
import ru.yandex.quasar.shadows.ShadowLogger
import java.util.concurrent.atomic.AtomicBoolean

@SuppressWarnings("unchecked")
@RunWith(RobolectricTestRunner::class)
@Config(shadows = [ShadowLogger::class], instrumentedPackages = ["ru.yandex.quasar.util"])
class MordoviaHomeScreenUpdaterTest {

    private lateinit var mordoviaHomeScreenRequester: MordoviaHomeScreenRequester
    private lateinit var mordoviaHomeScreenUpdater: MordoviaHomeScreenUpdater

    @Before
    fun runBeforeAnyTest() {
        mordoviaHomeScreenRequester = mock()
        mordoviaHomeScreenUpdater = MordoviaHomeScreenUpdater(mordoviaHomeScreenRequester, FakeMetricaReporter())
    }

    @Test
    fun given_noTaskInProgress_when_gotIncomingRequest_then_taskIsLaunchedAndCompleted() {
        val onCompleted = TestingOnCompletedCallback()
        val configuration = mock<MordoviaConfiguration>()

        // start request
        mordoviaHomeScreenUpdater.acquireFreshConfig(mock(), onCompleted)
        verify(mordoviaHomeScreenRequester).requestMegamindForced(any())

        // finish request
        Assert.assertTrue(mordoviaHomeScreenUpdater.handleMordoviaShow(configuration))

        // check that config is saved and callback is called
        verify(mordoviaHomeScreenRequester).persistConfiguration(configuration)
        onCompleted.assertWasCalled()
    }

    @Test
    fun given_firstTaskIsFinished_when_gotIncomingRequest_then_secondTaskIsLaunchedImmediately() {
        val onCompleted1 = TestingOnCompletedCallback()
        val onCompleted2 = TestingOnCompletedCallback()
        val configuration1 = mock<MordoviaConfiguration>()
        val configuration2 = mock<MordoviaConfiguration>()

        // start first request
        mordoviaHomeScreenUpdater.acquireFreshConfig(mock(), onCompleted1)
        verify(mordoviaHomeScreenRequester).requestMegamindForced(any())

        // finish first request
        Assert.assertTrue(mordoviaHomeScreenUpdater.handleMordoviaShow(configuration1))

        // check first request
        verify(mordoviaHomeScreenRequester).persistConfiguration(configuration1)
        onCompleted1.assertWasCalled()
        onCompleted2.assertWasNotCalled()

        // reset mock
        reset(mordoviaHomeScreenRequester)

        // start second request
        mordoviaHomeScreenUpdater.acquireFreshConfig(mock(), onCompleted2)
        verify(mordoviaHomeScreenRequester).requestMegamindForced(any())

        // finish second request
        Assert.assertTrue(mordoviaHomeScreenUpdater.handleMordoviaShow(configuration2))

        // check second request
        verify(mordoviaHomeScreenRequester, never()).persistConfiguration(configuration1)
        verify(mordoviaHomeScreenRequester).persistConfiguration(configuration2)
        onCompleted2.assertWasCalled()
    }

    @Test
    fun given_firstTaskInProgress_when_gotIncomingRequest_then_secondTaskIsLaunchedAfterFirst() {
        val onCompleted1 = TestingOnCompletedCallback()
        val onCompleted2 = TestingOnCompletedCallback()
        val configuration1 = mock<MordoviaConfiguration>()
        val configuration2 = mock<MordoviaConfiguration>()

        // start first request
        mordoviaHomeScreenUpdater.acquireFreshConfig(mock(), onCompleted1)
        verify(mordoviaHomeScreenRequester).requestMegamindForced(any())

        // prepare second request
        mordoviaHomeScreenUpdater.acquireFreshConfig(mock(), onCompleted2)
        verify(mordoviaHomeScreenRequester).requestMegamindForced(any())

        // finish first request
        Assert.assertTrue(mordoviaHomeScreenUpdater.handleMordoviaShow(configuration1))

        // check that first request is finished
        verify(mordoviaHomeScreenRequester).persistConfiguration(configuration1)
        onCompleted1.assertWasCalled()
        onCompleted2.assertWasNotCalled()

        // finish second request
        Assert.assertTrue(mordoviaHomeScreenUpdater.handleMordoviaShow(configuration2))

        // check that second request is finished
        verify(mordoviaHomeScreenRequester).persistConfiguration(configuration2)
        onCompleted2.assertWasCalled()
    }

    @Test
    fun given_taskIsFinished_when_handleMordoviaShowIsCalled_then_callbackNotCalledTwice() {
        val onCompleted = TestingOnCompletedCallback()
        val configuration1 = mock<MordoviaConfiguration>()
        val configuration2 = mock<MordoviaConfiguration>()

        // start request
        mordoviaHomeScreenUpdater.acquireFreshConfig(mock(), onCompleted)
        verify(mordoviaHomeScreenRequester).requestMegamindForced(any())

        // finish request
        Assert.assertTrue(mordoviaHomeScreenUpdater.handleMordoviaShow(configuration1))

        // check that request is finished
        verify(mordoviaHomeScreenRequester).persistConfiguration(configuration1)
        reset(mordoviaHomeScreenRequester)
        onCompleted.assertWasCalled()

        // check that callback is not called twice
        Assert.assertFalse(mordoviaHomeScreenUpdater.handleMordoviaShow(configuration1))
        Assert.assertFalse(mordoviaHomeScreenUpdater.handleMordoviaShow(configuration2))
        verify(mordoviaHomeScreenRequester, never()).persistConfiguration(any())
    }

    @Test
    fun given_taskInProgress_when_callbackIsDisposed_then_itShouldNotBeCalled() {
        val onCompleted = TestingOnCompletedCallback()
        val configuration = mock<MordoviaConfiguration>()

        // start request
        val disposable = mordoviaHomeScreenUpdater.acquireFreshConfig(mock(), onCompleted)
        verify(mordoviaHomeScreenRequester).requestMegamindForced(any())

        // dispose callback
        disposable.dispose()

        // finish request
        Assert.assertTrue(mordoviaHomeScreenUpdater.handleMordoviaShow(configuration))
        verify(mordoviaHomeScreenRequester).persistConfiguration(configuration)

        // assert
        onCompleted.assertWasNotCalled()
    }

    @Test
    fun given_twoCallbacks_when_oneCallbackIsDisposed_then_itShouldNotBeCalled_butOtherOneShould() {
        val onCompleted1 = TestingOnCompletedCallback()
        val onCompleted2 = TestingOnCompletedCallback()
        val configuration = mock<MordoviaConfiguration>()

        // launch first request
        mordoviaHomeScreenUpdater.acquireFreshConfig(mock(), mock())

        // prepare second request
        val disposable1 = mordoviaHomeScreenUpdater.acquireFreshConfig(mock(), onCompleted1)
        mordoviaHomeScreenUpdater.acquireFreshConfig(mock(), onCompleted2)

        // finish first request
        Assert.assertTrue(mordoviaHomeScreenUpdater.handleMordoviaShow(configuration))
        verify(mordoviaHomeScreenRequester).persistConfiguration(configuration)

        disposable1.dispose()

        // finish second request
        Assert.assertTrue(mordoviaHomeScreenUpdater.handleMordoviaShow(configuration))
        verify(mordoviaHomeScreenRequester, times(2)).persistConfiguration(configuration)

        // assert
        onCompleted1.assertWasNotCalled()
        onCompleted2.assertWasCalled()
    }

    private class TestingOnCompletedCallback : Runnable {
        private val isCompleted = AtomicBoolean(false)

        override fun run() {
            if (!isCompleted.compareAndSet(false, true)) {
                Assert.fail("onCompleted callback was called twice")
            }
        }

        fun assertWasCalled() = Assert.assertTrue(isCompleted.get())
        fun assertWasNotCalled() = Assert.assertFalse(isCompleted.get())
    }
}
