package ru.yandex.quasar.app.screensaver

import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.AdditionalMatchers.not
import org.mockito.ArgumentMatchers.eq
import org.mockito.kotlin.any
import org.mockito.kotlin.argumentCaptor
import org.mockito.kotlin.inOrder
import org.mockito.kotlin.mock
import org.mockito.kotlin.never
import org.mockito.kotlin.reset
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import ru.yandex.quasar.shadows.ShadowThreadUtil
import ru.yandex.quasar.app.screensaver.screenSaverConfigurators.ScreenSaverConfiguratorService
import ru.yandex.quasar.app.screensaver.screenSaverHelpers.ScreenSaverMediaLoader
import ru.yandex.quasar.app.screensaver.screenSaverMediaItems.ScreenSaverDiskItem

@RunWith(RobolectricTestRunner::class)
@Config(shadows = [ShadowThreadUtil::class], instrumentedPackages = ["ru.yandex.quasar.concurrency"])
class ScreenSaverPreparerTest {
    private val configuratorService: ScreenSaverConfiguratorService = mock()
    private val mediaLoader: ScreenSaverMediaLoader = mock()
    private val preparationListener: ScreenSaverPreparer.PreparationListener = mock()

    @Before
    fun setUp() {
        whenever(configuratorService.screenSaverMediaLoader).thenReturn(mediaLoader)
    }

    @Test
    fun given_preparer_when_init_then_startImmediateLoading() {
        // create preparer
        val preparer = ScreenSaverPreparer(configuratorService)

        // init
        preparer.init(preparationListener)

        // should subscribe on mediaLoader and start immediate loading
        verify(mediaLoader).addListener(any())
        verify(configuratorService).delayUpdate(eq(0))
    }

    @Test
    fun given_initializedPreparer_when_preparationFinished_then_listenerInvoked() {
        // create preparer and init with listener
        val preparer = ScreenSaverPreparer(configuratorService)
        preparer.init(preparationListener)

        // capture subscription to mediaLoader and call onMediaLoaded
        argumentCaptor<ScreenSaverMediaLoader.MediaLoadListener> {
            verify(mediaLoader).addListener(capture())
            val mediaLoadListener = firstValue
            mediaLoadListener.onMediaLoaded(
                ScreenSaverDiskItem(),
                ScreenSaverMediaLoader.ScreenSaverItemSource.CACHE
            )
        }

        // verify preparation listener has been invoked
        verify(preparationListener).onPreparationFinished()
    }

    @Test
    fun given_initializedPreparer_when_preparationFailed_then_delayUpdate() {
        // create preparer and init with listener
        val preparer = ScreenSaverPreparer(configuratorService)
        preparer.init(preparationListener)

        // capture subscription to mediaLoader and call onLoadFailed
        argumentCaptor<ScreenSaverMediaLoader.MediaLoadListener> {
            verify(mediaLoader).addListener(capture())
            val mediaLoadListener = firstValue
            mediaLoadListener.onLoadFailed()
        }

        // verify preparation listener has not been invoked and we scheduled next update
        verify(configuratorService).delayUpdate(not(eq(0)))
        verify(preparationListener, never()).onPreparationFinished()
    }

    @Test
    fun given_initializedPreparer_when_destroy_then_allDestroyed() {
        // create preparer and init with listener
        val preparer = ScreenSaverPreparer(configuratorService)
        preparer.init(preparationListener)

        // destroy preparer
        preparer.destroy()

        // unsubscribe and destroy
        inOrder(mediaLoader, configuratorService) {
            verify(mediaLoader).removeListener(any())
            verify(configuratorService).destroy()
        }
    }

    @Test
    fun given_destroyedPreparer_when_onMediaLoaded_then_nothingHappened() {
        // create preparer, init with listener and destroy
        val preparer = ScreenSaverPreparer(configuratorService)
        preparer.init(preparationListener)
        preparer.destroy()
        reset(preparationListener)

        // capture subscription to media loader and invoke onMediaLoaded
        argumentCaptor<ScreenSaverMediaLoader.MediaLoadListener> {
            verify(mediaLoader).addListener(capture())
            val mediaLoadListener = firstValue
            mediaLoadListener.onMediaLoaded(
                ScreenSaverDiskItem(),
                ScreenSaverMediaLoader.ScreenSaverItemSource.CACHE
            )
        }

        // nothing should happen
        verify(preparationListener, never()).onPreparationFinished()
    }

    @Test
    fun given_destroyedPreparer_when_onLoadFailed_then_nothingHappen() {
        // create preparer, init with listener and destroy
        val preparer = ScreenSaverPreparer(configuratorService)
        preparer.init(preparationListener)
        preparer.destroy()
        reset(configuratorService)

        // capture subscription to media loader and invoke onLoadFailed
        argumentCaptor<ScreenSaverMediaLoader.MediaLoadListener> {
            verify(mediaLoader).addListener(capture())
            val mediaLoadListener = firstValue
            mediaLoadListener.onLoadFailed()
        }

        // nothing should happen
        verify(configuratorService, never()).delayUpdate(any())
    }
}
