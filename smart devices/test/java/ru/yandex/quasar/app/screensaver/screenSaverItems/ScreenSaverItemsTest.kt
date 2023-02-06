package ru.yandex.quasar.app.screensaver.screenSaverItems

import org.junit.Assert.*
import org.junit.Test

class ScreenSaverItemsTest {
    @Test
    fun given_imageItemWithEmptyUrl_when_isValid_then_false() {
        val videoItem = ScreenSaverImageItem("")
        assertFalse(videoItem.isValid)
    }

    @Test
    fun given_videoItemWithEmptyUrl_when_isValid_then_false() {
        val videoItem = ScreenSaverVideoItem("")
        assertFalse(videoItem.isValid)
    }

    @Test
    fun given_imageItemWithNonEmptyUrl_when_isValid_then_true() {
        val videoItem = ScreenSaverImageItem("testUrl")
        assertTrue(videoItem.isValid)
    }

    @Test
    fun given_videoItemWithNonEmptyUrl_when_isValid_then_true() {
        val videoItem = ScreenSaverVideoItem("testUrl")
        assertTrue(videoItem.isValid)
    }

    @Test
    fun given_imageItem_when_compareWithItself_then_equals() {
        val imageItem1 = ScreenSaverImageItem("")
        val imageItem2 = ScreenSaverImageItem("testUrl")

        assertEquals(imageItem1, imageItem1)
        assertEquals(imageItem2, imageItem2)
    }

    @Test
    fun given_videoItem_when_compareWithItself_then_equals() {
        val videoItem1 = ScreenSaverVideoItem("")
        val videoItem2 = ScreenSaverVideoItem("testUrl")

        assertEquals(videoItem1, videoItem1)
        assertEquals(videoItem2, videoItem2)
    }

    @Test
    fun given_imageItemsWithEqualUrl_when_compare_then_equals() {
        val imageItem1 = ScreenSaverImageItem("testUrl")
        val imageItem2 = ScreenSaverImageItem("testUrl")
        val imageItem3 = ScreenSaverImageItem("")
        val imageItem4 = ScreenSaverImageItem("")

        assertEquals(imageItem1, imageItem2)
        assertEquals(imageItem3, imageItem4)
    }

    @Test
    fun given_videoItemsWithEqualUrl_when_compare_then_equals() {
        val videoItem1 = ScreenSaverVideoItem("testUrl")
        val videoItem2 = ScreenSaverVideoItem("testUrl")
        val videoItem3 = ScreenSaverVideoItem("")
        val videoItem4 = ScreenSaverVideoItem("")

        assertEquals(videoItem1, videoItem2)
        assertEquals(videoItem3, videoItem4)
    }

    @Test
    fun given_imageItemsWithDifferentUrls_when_compare_then_notEquals() {
        val imageItem1 = ScreenSaverImageItem("testUrl1")
        val imageItem2 = ScreenSaverImageItem("testUrl2")
        val imageItem3 = ScreenSaverImageItem("")

        assertNotEquals(imageItem1, imageItem2)
        assertNotEquals(imageItem1, imageItem3)
    }

    @Test
    fun given_videoItemsWithDifferentUrls_when_compare_then_notEquals() {
        val videoItem1 = ScreenSaverVideoItem("testUrl1")
        val videoItem2 = ScreenSaverVideoItem("testUrl2")
        val videoItem3 = ScreenSaverVideoItem("")

        assertNotEquals(videoItem1, videoItem2)
        assertNotEquals(videoItem1, videoItem3)
    }

    @Test
    fun given_imageItemAndTestItem_when_compare_then_notEquals() {
        val imageItem1 = ScreenSaverImageItem("testUrl")
        val testItem1 = TestScreenSaverItem("testUrl")
        val testItem2 = TestScreenSaverItem("")

        assertNotEquals(imageItem1, testItem1)
        assertNotEquals(imageItem1, testItem2)
    }

    @Test
    fun given_videoItemAndTestItem_when_compare_then_notEquals() {
        val videoItem1 = ScreenSaverVideoItem("testUrl")
        val testItem1 = TestScreenSaverItem("testUrl")
        val testItem2 = TestScreenSaverItem("")

        assertNotEquals(videoItem1, testItem1)
        assertNotEquals(videoItem1, testItem2)
    }
}