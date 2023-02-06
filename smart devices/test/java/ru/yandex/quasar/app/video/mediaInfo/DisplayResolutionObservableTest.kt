package ru.yandex.quasar.app.video.mediaInfo

import org.junit.Assert
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import ru.yandex.quasar.shadows.ShadowThreadUtil


@RunWith(RobolectricTestRunner::class)
@Config(
        shadows = [ShadowThreadUtil::class],
        instrumentedPackages = ["ru.yandex.quasar.concurrency"]
)
class DisplayResolutionObservableTest {

    private val displayResolutionPath = ""
    private val displayResolutionObservable = DisplayResolutionObservable(displayResolutionPath)

    @Test
    fun when_correctFormat_then_getDisplayResolution() {
        Assert.assertEquals(1080, displayResolutionObservable.parseDisplayResolution("1080p60z"))
        Assert.assertEquals(576, displayResolutionObservable.parseDisplayResolution("576cvs"))
        Assert.assertEquals(2160, displayResolutionObservable.parseDisplayResolution("2160p60z"))
        Assert.assertEquals(1080, displayResolutionObservable.parseDisplayResolution("1080p"))
        Assert.assertEquals(1080, displayResolutionObservable.parseDisplayResolution("1080"))
    }

    @Test
    fun when_incorrectFormat_then_getNull() {
        Assert.assertEquals(null, displayResolutionObservable.parseDisplayResolution(""))
        Assert.assertEquals(null, displayResolutionObservable.parseDisplayResolution("p60z"))
        Assert.assertEquals(null, displayResolutionObservable.parseDisplayResolution("cvs"))
    }
}
