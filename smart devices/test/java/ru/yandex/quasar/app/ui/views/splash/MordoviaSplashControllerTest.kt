package ru.yandex.quasar.app.ui.views.splash

import org.junit.Before
import org.junit.Test
import org.mockito.Mock
import org.mockito.kotlin.never
import org.mockito.kotlin.reset
import org.mockito.kotlin.times
import org.mockito.kotlin.verify
import org.robolectric.annotation.Config
import ru.yandex.quasar.BaseTest
import ru.yandex.quasar.shadows.ShadowLogger

@Config(shadows = [ShadowLogger::class], instrumentedPackages = ["ru.yandex.quasar.util"])
class MordoviaSplashControllerTest : BaseTest() {

    @Mock
    private lateinit var viewMock: MordoviaSplashView

    private lateinit var controller: MordoviaSplashController

    @Before
    fun setUp() {
        controller = MordoviaSplashController()
        controller.view = viewMock
        reset(viewMock)
    }

    @Test
    fun given_initialState_when_showSplash_then_showIsCalled() {
        // act
        controller.showSplash()

        // assert
        verify(viewMock, never()).hide()
        verify(viewMock, times(1)).show()
    }

    @Test
    fun given_initialState_when_pageReady_then_showIsCalled() {
        // act
        controller.onPageReady()

        // assert
        verify(viewMock, never()).hide()
        verify(viewMock, times(1)).show()
    }

    @Test
    fun given_initialState_when_contentReady_then_showIsCalled() {
        // act
        controller.onContentReady()

        // assert
        verify(viewMock, never()).hide()
        verify(viewMock, times(1)).show()
    }

    @Test
    fun given_contentReady_when_pageReady_then_hideIsCalled() {
        // setup
        controller.onContentReady()
        reset(viewMock)

        // act
        controller.onPageReady()

        // assert
        verify(viewMock, times(1)).hide()
        verify(viewMock, never()).show()
    }

    @Test
    fun given_pageReady_when_contentReady_then_hideIsCalled() {
        // setup
        controller.onPageReady()
        reset(viewMock)

        // act
        controller.onContentReady()

        // assert
        verify(viewMock, times(1)).hide()
        verify(viewMock, never()).show()
    }

    @Test
    fun given_pageAndContentReady_when_showSplash_then_showIsCalled() {
        // setup
        controller.onContentReady()
        controller.onPageReady()
        reset(viewMock)

        // act
        controller.showSplash()

        // assert
        verify(viewMock, times(1)).show()
        verify(viewMock, never()).hide()
    }

    @Test
    fun given_pageAndContentReady_when_contentReady_then_hideIsCalled() {
        // setup
        controller.onContentReady()
        controller.onPageReady()
        reset(viewMock)

        // act
        controller.onContentReady()

        // assert
        verify(viewMock, never()).show()
        verify(viewMock, times(1)).hide()
    }

    @Test
    fun given_pageAndContentReady_when_pageReady_then_hideIsCalled() {
        // setup
        controller.onContentReady()
        controller.onPageReady()
        reset(viewMock)

        // act
        controller.onPageReady()

        // assert
        verify(viewMock, never()).show()
        verify(viewMock, times(1)).hide()
    }

    @Test
    fun given_initialState_when_viewIsSet_then_showIsCalled() {
        // act
        controller.view = viewMock

        // assert
        verify(viewMock, never()).hide()
        verify(viewMock, times(1)).show()
    }

    @Test
    fun given_pageAndContentReady_when_viewIsSet_then_hideIsCalled() {
        // setup
        controller.onPageReady()
        controller.onContentReady()
        reset(viewMock)

        // act
        controller.view = viewMock

        // assert
        verify(viewMock, times(1)).hide()
        verify(viewMock, never()).show()
    }
}
