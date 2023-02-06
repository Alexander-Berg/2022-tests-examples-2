package ru.yandex.quasar.app.screensaver.screenSaverItems

import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import ru.yandex.quasar.app.screensaver.screenSaverItems.ScreenSaverImageItem
import ru.yandex.quasar.app.screensaver.screenSaverItems.ScreenSaverItem
import ru.yandex.quasar.app.screensaver.screenSaverItems.ScreenSaverItemsCollection
import ru.yandex.quasar.app.screensaver.screenSaverItems.ScreenSaverVideoItem

class ScreenSaverItemsCollectionTest {

    private val items: List<ScreenSaverItem>

    init {
        val image1 = ScreenSaverImageItem("image1")
        val image2 = ScreenSaverImageItem("image2")
        val video1 = ScreenSaverVideoItem("video1")
        val video2 = ScreenSaverVideoItem("video2")
        items = listOf(image1, video1, image2, video2)
    }

    @Test
    fun given_emptyCollection_when_setStartPosition_then_startPositionIsZero() {
        val screenSaverCollection = ScreenSaverItemsCollection(listOf())

        assertEquals(0, screenSaverCollection.currentPosition)

        screenSaverCollection.setStartPosition(0)
        assertEquals(0, screenSaverCollection.currentPosition)

        screenSaverCollection.setStartPosition(1)
        assertEquals(0, screenSaverCollection.currentPosition)

        screenSaverCollection.setStartPosition(-1)
        assertEquals(0, screenSaverCollection.currentPosition)
    }

    @Test
    fun given_collectionWithItems_when_setStartPosition_then_currentPositionIsCorrect() {
        val screenSaverCollection = ScreenSaverItemsCollection(items)

        assertEquals(0, screenSaverCollection.currentPosition)
        assertEquals(items[0], screenSaverCollection.next)

        screenSaverCollection.setStartPosition(2)
        assertEquals(2, screenSaverCollection.currentPosition)

        screenSaverCollection.setStartPosition(3)
        assertEquals(3, screenSaverCollection.currentPosition)

        screenSaverCollection.setStartPosition(10)
        // start position is greater than collection size, nothing should changed
        assertEquals(3, screenSaverCollection.currentPosition)

        screenSaverCollection.setStartPosition(-1)
        // start position is lesser than zero, nothing should changed
        assertEquals(3, screenSaverCollection.currentPosition)
    }

    @Test
    fun given_collectionWithItems_when_setStartPosition_then_nextItemIsCorrect() {
        val screenSaverCollection = ScreenSaverItemsCollection(items)

        assertEquals(items[0], screenSaverCollection.next)

        screenSaverCollection.setStartPosition(2)
        assertEquals(items[2], screenSaverCollection.next)

        screenSaverCollection.setStartPosition(3)
        assertEquals(items[3], screenSaverCollection.next)

        screenSaverCollection.setStartPosition(10)
        // start position is greater than collection size, nothing should changed
        assertEquals(items[0], screenSaverCollection.next)

        screenSaverCollection.setStartPosition(0)
        assertEquals(items[0], screenSaverCollection.next)
    }

    @Test
    fun given_collectionWithItems_when_getNext_when_nextItemIsCorrect() {
        val screenSaverCollection = ScreenSaverItemsCollection(items)
        for (i in 0..items.size) {
            assertEquals(i % items.size, screenSaverCollection.currentPosition)
            assertEquals(items[i % items.size], screenSaverCollection.next)
        }
        assertEquals(1, screenSaverCollection.currentPosition)
        assertEquals(items[1], screenSaverCollection.next)
    }

    @Test
    fun given_emptyCollection_when_getNext_when_nextItemIsNull() {
        val emptyCollection = ScreenSaverItemsCollection(listOf())
        assertNull(emptyCollection.next)
    }
}