package ru.yandex.quasar.app.screensaver.screenSaverHelpers

import org.junit.Test
import org.mockito.Mockito.verify
import org.mockito.kotlin.mock

class ScreenSaverImageLoaderTest {
    @Test
    fun given_imageLoader_when_destroy_then_picassoWrapperShouldShutdown() {
        // mock picassoWrapper and create ScreenSaverImageLoader
        val picassoWrapper: ScreenSaverPicassoWrapper = mock()
        val imageLoader = ScreenSaverImageLoader(picassoWrapper)

        // destroy image loader
        imageLoader.destroy()

        // verify picassoWrapper.shutdown() has been called
        verify(picassoWrapper).shutdown()
    }
}
