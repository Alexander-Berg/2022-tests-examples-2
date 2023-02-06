package com.yandex.tv.videoplayer.common.utils

import org.junit.Test
import java.util.concurrent.TimeUnit

class TextUtilsTest {

    @Test
    fun compareTimes() {
        assertEquals("0:00", 0)
        assertEquals("0:07", 7)
        assertEquals("9:00", TimeUnit.MINUTES.toSeconds(9))
        assertEquals("10:00", TimeUnit.MINUTES.toSeconds(10))
        assertEquals("11:00", TimeUnit.MINUTES.toSeconds(11))
        assertEquals("1:00:00", TimeUnit.HOURS.toSeconds(1))
        assertEquals("1:07:00", TimeUnit.HOURS.toSeconds(1) + TimeUnit.MINUTES.toSeconds(7))
        assertEquals("1:37:00", TimeUnit.HOURS.toSeconds(1) + TimeUnit.MINUTES.toSeconds(37))
        assertEquals("4:27:00", TimeUnit.HOURS.toSeconds(4) + TimeUnit.MINUTES.toSeconds(27))
        assertEquals("120:37:00", TimeUnit.HOURS.toSeconds(120) + TimeUnit.MINUTES.toSeconds(37))
    }

    private fun assertEquals(expected: String, timeSec: Long) {
        org.junit.Assert.assertEquals(expected, TextUtils.getTimeText(timeSec))
    }
}