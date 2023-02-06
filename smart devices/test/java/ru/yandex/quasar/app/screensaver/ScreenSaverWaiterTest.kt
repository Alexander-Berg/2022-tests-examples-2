package ru.yandex.quasar.app.screensaver

import android.os.Handler
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.any
import org.mockito.kotlin.argumentCaptor
import org.mockito.kotlin.eq
import org.mockito.kotlin.mock
import org.mockito.kotlin.never
import org.mockito.kotlin.reset
import org.mockito.kotlin.spy
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.powermock.api.mockito.PowerMockito
import org.powermock.core.classloader.annotations.PrepareForTest
import org.powermock.modules.junit4.PowerMockRunner
import ru.yandex.quasar.app.dagger.activity.screensaver.ScreenSaverComponent
import ru.yandex.quasar.app.dagger.activity.screensaver.ScreenSaverComponentHolder

@RunWith(PowerMockRunner::class)
@PrepareForTest(ScreenSaverWaiter::class)
class ScreenSaverWaiterTest {

    private val componentFactory: ScreenSaverComponent.Factory = mock()
    private val componentHolder = ScreenSaverComponentHolder(componentFactory)
    private val component: ScreenSaverComponent = mock()
    private val preparer: ScreenSaverPreparer = mock()
    private val handler: Handler = mock()
    private lateinit var waiter: ScreenSaverWaiter

    @Before
    fun setUp() {
        PowerMockito.whenNew(Handler::class.java).withAnyArguments().thenReturn(handler)
        whenever(componentFactory.build()).thenReturn(component)
        whenever(component.getScreenSaverPreparer()).thenReturn(preparer)
    }

    private fun initWaiter(waitBefore: Long = 5 * 60 * 1000) {
        waiter = ScreenSaverWaiter(componentHolder, waitBefore, mock())
    }

    @Test
    fun given_waiter_when_stopWait_then_nothingHappened() {
        // create waiter
        initWaiter()

        // stop after creation
        waiter.stopWait()

        // nothing should happen
        verify(handler, never()).removeCallbacksAndMessages(eq(null))
        verify(handler, never()).postDelayed(any(), any())
    }

    @Test
    fun given_waiter_when_startWait_then_waitingStarted() {
        // create waiter
        initWaiter()

        // start wait
        waiter.startWait()

        // waiting has been started
        verify(handler).removeCallbacksAndMessages(eq(null))
        verify(handler).postDelayed(any(), any())
    }

    @Test
    fun given_startedWaiter_when_startWait_then_nothingHappened() {
        // create waiter and start wait
        initWaiter()
        waiter.startWait()
        reset(handler)

        // start again
        waiter.startWait()

        // nothing should happen
        verify(handler, never()).removeCallbacksAndMessages(eq(null))
        verify(handler, never()).postDelayed(any(), any())
    }

    @Test
    fun given_startedWaiter_when_stopWait_then_waitingStopped() {
        // create waiter and start wait
        initWaiter()
        waiter.startWait()
        reset(handler)

        // stop waiter
        waiter.stopWait()

        // waiting has been stopped
        verify(handler).removeCallbacksAndMessages(eq(null))
        verify(handler, never()).postDelayed(any(), any())
    }

    @Test
    fun given_stoppedWaiter_when_stopWait_then_nothingHappened() {
        // create waiter, start and stop it
        initWaiter()
        waiter.startWait()
        waiter.stopWait()
        reset(handler)

        // stop again
        waiter.stopWait()

        // nothing should happened
        verify(handler, never()).removeCallbacksAndMessages(eq(null))
        verify(handler, never()).postDelayed(any(), any())
    }

    @Test
    fun given_stoppedWaiter_when_startWait_then_waitingStarted() {
        // create waiter, start and stop it
        initWaiter()
        waiter.startWait()
        waiter.stopWait()
        reset(handler)

        // start waiter
        waiter.startWait()

        // waiting started
        verify(handler).removeCallbacksAndMessages(eq(null))
        verify(handler).postDelayed(any(), any())
    }

    @Test
    fun given_waiter_when_resetTimer_then_waitingStarted() {
        // create spy for waiter
        val spyWaiter = spy(ScreenSaverWaiter(componentHolder, 0, mock()))
        reset(spyWaiter)

        // reset waiter
        spyWaiter.resetTimer()

        // waiting has been started
        verify(spyWaiter).startWait()
    }

    @Test
    fun given_startedWaiter_when_resetTimer_then_waitingNotRestarted() {
        // create spy for waiter
        val spyWaiter = spy(ScreenSaverWaiter(componentHolder, 0, mock()))
        spyWaiter.startWait()
        reset(spyWaiter)

        // reset waiter
        spyWaiter.resetTimer()

        // waiting hasn't been restarted
        verify(spyWaiter, never()).startWait()
    }

    @Test
    fun given_stoppedWaiter_when_resetTimer_then_waitingStarted() {
        // create spy for waiter
        val spyWaiter = spy(ScreenSaverWaiter(componentHolder, 0, mock()))
        initWaiter()
        spyWaiter.startWait()
        spyWaiter.stopWait()
        reset(spyWaiter)

        // reset waiter
        spyWaiter.resetTimer()

        // waiting has been started
        verify(spyWaiter).startWait()
    }

    @Test
    fun given_waiterWithZeroSecondsBeforeShowing_when_startWait_then_initScreenSaver() {
        // create waiter with 0 seconds before start
        initWaiter(0)

        // start wait screensaver
        waiter.startWait()
        // capture check time task and run it
        argumentCaptor<Runnable> {
            verify(handler).postDelayed(capture(), any())
            val checkTime = firstValue
            checkTime.run()
        }

        // should start initializing screensaver
        verify(preparer).init(any())
    }

    @Test
    fun given_waiterWithFiveMinutesBeforeShowing_when_startWait_then_delayCalled() {
        // create waiter with 5 minutes before start
        initWaiter((5 * 60 * 1000).toLong())

        // start wait screensaver
        waiter.startWait()
        // capture check time task and run it
        lateinit var checkTime: Runnable
        argumentCaptor<Runnable> {
            verify(handler).postDelayed(capture(), any())
            checkTime = firstValue
        }
        reset(handler)
        checkTime.run()

        // shouldn't start initializing screensaver, should call postDelay
        verify(preparer, never()).init(any())
        verify(handler).postDelayed(any(), any())
    }

    @Test
    fun given_waiter_when_preparationFinished_then_timeoutListenerInvoked() {
        // create waiter with 0 seconds before start
        initWaiter(0)
        val timeOutListener: ScreenSaverWaiter.OnTimeOutListener = mock()
        waiter.setListener(timeOutListener)

        // start wait screensaver
        waiter.startWait()
        // capture check time task and run it
        lateinit var checkTime: Runnable
        argumentCaptor<Runnable> {
            verify(handler).postDelayed(capture(), any())
            checkTime = firstValue
            checkTime.run()
        }

        // capture listener ans finish preparation
        argumentCaptor<ScreenSaverPreparer.PreparationListener> {
            verify(preparer).init(capture())
            val onPreparationFinished = firstValue
            onPreparationFinished.onPreparationFinished()
        }

        // onTimeout has to be called
        verify(timeOutListener).onTimeout()
    }
}
