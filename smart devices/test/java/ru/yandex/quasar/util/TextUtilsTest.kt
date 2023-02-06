package ru.yandex.quasar.util

import org.junit.Assert
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner

@RunWith(RobolectricTestRunner::class)
class TextUtilsTest {
    @Test
    fun maskTest() {
        Assert.assertEquals(TextUtils.mask("abcdefghij", 4), "******ghij")
        Assert.assertEquals(TextUtils.mask("abcdefghij", 1), "*********j")
        Assert.assertEquals(TextUtils.mask("abcdefghij", 0), "**********")
        Assert.assertEquals(TextUtils.mask("abcdefghij", -1), "**********")
        Assert.assertEquals(TextUtils.mask("abcdefghij", 10), "abcdefghij")
        Assert.assertEquals(TextUtils.mask("abcdefghij", 15), "abcdefghij")
        Assert.assertEquals(TextUtils.mask("", 0), "")
        Assert.assertEquals(TextUtils.mask("", 10), "")
        Assert.assertEquals(TextUtils.mask("", -1), "")

    }
}
