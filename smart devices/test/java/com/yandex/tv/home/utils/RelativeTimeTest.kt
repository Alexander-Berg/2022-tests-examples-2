package com.yandex.tv.home.utils

import android.os.Build
import com.yandex.tv.home.repository.RepositoryTestApp
import org.junit.Assert
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.util.concurrent.TimeUnit

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.P], application = RepositoryTestApp::class)
class RelativeTimeTest {

    @Test
    fun oneMinuteStartEventTest() {
        val now = System.currentTimeMillis()
        val eventTime = now + TimeUnit.MINUTES.toMillis(1)
        val duration = TimeUnit.MINUTES.toMillis(10)
        val relativeTime = TimeUtils.getRelativeTime(eventTime, duration, "Live", "in a minute")
        Assert.assertEquals(relativeTime, "in a minute")
    }

    @Test
    fun liveEventTest() {
        val now = System.currentTimeMillis()
        val eventTime = now - TimeUnit.MINUTES.toMillis(1)
        val duration = TimeUnit.MINUTES.toMillis(10)
        val relativeTime = TimeUtils.getRelativeTime(eventTime, duration, "Live", "in a minute")
        Assert.assertEquals(relativeTime, "Live")
    }

    @Test
    fun pastEventTest() {
        val now = System.currentTimeMillis()
        val duration = TimeUnit.MINUTES.toMillis(5)
        val eventTime = now - TimeUnit.MINUTES.toMillis(10)
        val relativeTime = TimeUtils.getRelativeTime(eventTime, duration, "Live", "in a minute")
        Assert.assertNotEquals(relativeTime, "Live")
        Assert.assertNotEquals(relativeTime, "in a minute")
    }
}
