package ru.yandex.quasar.app.screensaver.screenSaverHelpers.writers

import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.mockito.kotlin.spy
import ru.yandex.quasar.app.screensaver.screenSaverItems.ScreenSaverItem
import ru.yandex.quasar.app.screensaver.screenSaverItems.TestScreenSaverItem
import ru.yandex.quasar.app.screensaver.screenSaverMediaItems.TestMediaItem

class ScreenSaverWriterTest {
    lateinit var screenSaverWriter: TestWriter

    @Before
    fun setUp() {
        screenSaverWriter = TestWriter()
    }

    @Test
    fun given_writer_then_itemsNotLoaded() {
        // create media items
        val mediaItem1 = TestMediaItem(TestScreenSaverItem())
        val mediaItem2 = TestMediaItem(TestScreenSaverItem())

        // writer hasn't any items
        assertFalse(screenSaverWriter.hasNextItem())
        assertFalse(screenSaverWriter.isItemLoaded(mediaItem1.screenSaverInfo))
        assertFalse(screenSaverWriter.isItemLoaded(mediaItem2.screenSaverInfo))
    }

    @Test
    fun given_writer_when_addOneMediaItem_then_firstItemIsLoaded() {
        // create media items
        val mediaItem1 = TestMediaItem(TestScreenSaverItem())
        val mediaItem2 = TestMediaItem(TestScreenSaverItem())

        // add item
        screenSaverWriter.addItem(mediaItem1)

        // first item is loaded, second is not
        assertTrue(screenSaverWriter.hasNextItem())
        assertTrue(screenSaverWriter.isItemLoaded(mediaItem1.screenSaverInfo))
        assertFalse(screenSaverWriter.isItemLoaded(mediaItem2.screenSaverInfo))
    }

    @Test
    fun given_writer_when_addTwoMediaItems_then_bothItemsLoaded() {
        // create media items
        val mediaItem1 = TestMediaItem(TestScreenSaverItem())
        val mediaItem2 = TestMediaItem(TestScreenSaverItem())

        // add both items
        screenSaverWriter.addItem(mediaItem1)
        screenSaverWriter.addItem(mediaItem2)

        // both items are loaded
        assertTrue(screenSaverWriter.hasNextItem())
        assertTrue(screenSaverWriter.isItemLoaded(mediaItem1.screenSaverInfo))
        assertTrue(screenSaverWriter.isItemLoaded(mediaItem2.screenSaverInfo))
    }

    @Test
    fun given_writer_when_addMediaItemTwice_then_bothItemsLoaded() {
        // create media items
        val mediaItem1 = TestMediaItem(TestScreenSaverItem())
        val mediaItem2 = TestMediaItem(TestScreenSaverItem())

        // add first item twice
        screenSaverWriter.addItem(mediaItem1)
        screenSaverWriter.addItem(mediaItem1)
        screenSaverWriter.addItem(mediaItem2)

        // no exception and both items are loaded
        assertTrue(screenSaverWriter.hasNextItem())
        assertTrue(screenSaverWriter.isItemLoaded(mediaItem1.screenSaverInfo))
        assertTrue(screenSaverWriter.isItemLoaded(mediaItem2.screenSaverInfo))
    }

    @Test
    fun given_writer_when_addItemsWithEqualInfo_then_bothItemsLoaded() {
        // create media items with equal screen saver info
        val info = TestScreenSaverItem()
        val mediaItem1 = TestMediaItem(info)
        val mediaItem2 = TestMediaItem(info)

        // add both items
        screenSaverWriter.addItem(mediaItem1)
        screenSaverWriter.addItem(mediaItem2)

        // no exception and both items are loaded
        assertTrue(screenSaverWriter.hasNextItem())
        assertTrue(screenSaverWriter.isItemLoaded(mediaItem1.screenSaverInfo))
        assertTrue(screenSaverWriter.isItemLoaded(mediaItem2.screenSaverInfo))
    }

    @Test
    fun given_writerWithNoItems_when_removeMediaItem_then_itemsNotLoaded() {
        // create items and don't add them
        val mediaItem1 = TestMediaItem(TestScreenSaverItem())
        val mediaItem2 = TestMediaItem(TestScreenSaverItem())

        // remove first item (it is not loaded)
        screenSaverWriter.remove(mediaItem1)

        // no exception and writer has no items
        assertFalse(screenSaverWriter.hasNextItem())
        assertFalse(screenSaverWriter.isItemLoaded(mediaItem1.screenSaverInfo))
        assertFalse(screenSaverWriter.isItemLoaded(mediaItem2.screenSaverInfo))
    }

    @Test
    fun given_writerWithItems_when_removeMediaItem_then_removedItemIsNotLoaded() {
        // create items and add them
        val mediaItem1 = TestMediaItem(TestScreenSaverItem())
        val mediaItem2 = TestMediaItem(TestScreenSaverItem())
        screenSaverWriter.addItem(mediaItem1)
        screenSaverWriter.addItem(mediaItem2)

        // remove second item
        screenSaverWriter.remove(mediaItem2)

        // first item is loaded, but second is not
        assertTrue(screenSaverWriter.hasNextItem())
        assertTrue(screenSaverWriter.isItemLoaded(mediaItem1.screenSaverInfo))
        assertFalse(screenSaverWriter.isItemLoaded(mediaItem2.screenSaverInfo))
    }

    @Test
    fun given_writerWithRepeatedItem_when_removeRepeatedMediaItem_then_itemIsNotLoaded() {
        // create media items and add first twice
        val mediaItem1 = TestMediaItem(TestScreenSaverItem())
        val mediaItem2 = TestMediaItem(TestScreenSaverItem())
        screenSaverWriter.addItem(mediaItem1)
        screenSaverWriter.addItem(mediaItem1)
        screenSaverWriter.addItem(mediaItem2)

        // remove first item
        screenSaverWriter.remove(mediaItem1)

        // first item is not loaded, but second is
        assertTrue(screenSaverWriter.hasNextItem())
        assertFalse(screenSaverWriter.isItemLoaded(mediaItem1.screenSaverInfo))
        assertTrue(screenSaverWriter.isItemLoaded(mediaItem2.screenSaverInfo))
    }

    @Test
    fun given_writerItems_when_removeAllMediaItems_then_itemsIsNotLoaded() {
        // create items and add them
        val mediaItem1 = TestMediaItem(TestScreenSaverItem())
        val mediaItem2 = TestMediaItem(TestScreenSaverItem())
        screenSaverWriter.addItem(mediaItem1)
        screenSaverWriter.addItem(mediaItem1)
        screenSaverWriter.addItem(mediaItem2)

        // remove both items
        screenSaverWriter.remove(mediaItem1)
        screenSaverWriter.remove(mediaItem2)

        // items is not loaded
        assertFalse(screenSaverWriter.hasNextItem())
        assertFalse(screenSaverWriter.isItemLoaded(mediaItem1.screenSaverInfo))
        assertFalse(screenSaverWriter.isItemLoaded(mediaItem2.screenSaverInfo))
    }

    @Test
    fun given_writerWithNoItems_when_removeItem_itemsNotLoaded() {
        // create screen saver items

        val item1: ScreenSaverItem = TestScreenSaverItem()
        val item2: ScreenSaverItem = TestScreenSaverItem()

        // remove first item
        screenSaverWriter.remove(item1)

        // no items are loaded
        assertFalse(screenSaverWriter.hasNextItem())
        assertFalse(screenSaverWriter.isItemLoaded(item1))
        assertFalse(screenSaverWriter.isItemLoaded(item2))
    }

    @Test
    fun given_writerWithAddedItems_when_removeOneItem_firstItemIsNotLoaded() {
        // create screen saver items and media items and add them
        val item1: ScreenSaverItem = TestScreenSaverItem()
        val mediaItem1 = TestMediaItem(item1)
        val item2: ScreenSaverItem = TestScreenSaverItem()
        val mediaItem2 = TestMediaItem(item2)
        screenSaverWriter.addItem(mediaItem1)
        screenSaverWriter.addItem(mediaItem2)

        // remove first item
        screenSaverWriter.remove(item1)

        // first item is not loaded, but second is
        assertTrue(screenSaverWriter.hasNextItem())
        assertFalse(screenSaverWriter.isItemLoaded(item1))
        assertTrue(screenSaverWriter.isItemLoaded(item2))
    }

    @Test
    fun given_writerWithRepeatedItem_when_removeRepeatedItem_repeatedItemIsNotLoaded() {
        // create screen saver items and media items and add them
        val item1: ScreenSaverItem = TestScreenSaverItem()
        val mediaItem1 = TestMediaItem(item1)
        val item2: ScreenSaverItem = TestScreenSaverItem()
        val mediaItem2 = TestMediaItem(item2)
        screenSaverWriter.addItem(mediaItem1)
        screenSaverWriter.addItem(mediaItem2)
        screenSaverWriter.addItem(mediaItem2)

        // remove repeated item
        screenSaverWriter.remove(item2)

        // first item is loaded, but second is not
        assertTrue(screenSaverWriter.hasNextItem())
        assertTrue(screenSaverWriter.isItemLoaded(item1))
        assertFalse(screenSaverWriter.isItemLoaded(item2))
    }

    @Test
    fun given_writerWithItemsWithEqualInfo_when_removeItemWithEqualInfo_itemsWithEqualInfoAreNotLoaded() {
        // create screen saver items and media items and add them
        val item1: ScreenSaverItem = TestScreenSaverItem()
        val mediaItem1 = TestMediaItem(item1)
        val item2: ScreenSaverItem = TestScreenSaverItem()
        val mediaItem2 = TestMediaItem(item2)
        val mediaItem3 = TestMediaItem(item2) // same info as in mediaItem2
        screenSaverWriter.addItem(mediaItem1)
        screenSaverWriter.addItem(mediaItem2)
        screenSaverWriter.addItem(mediaItem3)

        // remove second item
        screenSaverWriter.remove(item2)

        // first item is loaded, but second is not
        assertTrue(screenSaverWriter.hasNextItem())
        assertTrue(screenSaverWriter.isItemLoaded(item1))
        assertFalse(screenSaverWriter.isItemLoaded(item2))
    }

    @Test
    fun given_writerWithoutItems_when_addItems_then_usedMemoryIsCorrect() {
        // create media items
        val mediaItem1 = TestMediaItem(TestScreenSaverItem(), size = 10)
        val mediaItem2 = TestMediaItem(TestScreenSaverItem(), size = 20)
        val mediaItem3 = TestMediaItem(TestScreenSaverItem(), size = 30)

        // add items and check getUsedMemory work correctly
        assertEquals(0, screenSaverWriter.getUsedMemory())
        screenSaverWriter.addItem(mediaItem1)
        assertEquals(10, screenSaverWriter.getUsedMemory())
        screenSaverWriter.addItem(mediaItem2)
        assertEquals(30, screenSaverWriter.getUsedMemory())
        screenSaverWriter.addItem(mediaItem3)
        assertEquals(60, screenSaverWriter.getUsedMemory())
        screenSaverWriter.addItem(mediaItem3)
        assertEquals(60, screenSaverWriter.getUsedMemory())
    }

    @Test
    fun given_writerWithAddedItems_when_removeItems_then_usedMemoryIsCorrect() {
        // create media items and add them
        val mediaItem1 = TestMediaItem(TestScreenSaverItem(), size = 10)
        val mediaItem2 = TestMediaItem(TestScreenSaverItem(), size = 20)
        val mediaItem3 = TestMediaItem(TestScreenSaverItem(), size = 30)
        screenSaverWriter.addItem(mediaItem1)
        screenSaverWriter.addItem(mediaItem2)
        screenSaverWriter.addItem(mediaItem3)

        // remove items and check getUsedMemory work correctly
        screenSaverWriter.remove(mediaItem2)
        assertEquals(40, screenSaverWriter.getUsedMemory())
        screenSaverWriter.remove(mediaItem2)
        assertEquals(40, screenSaverWriter.getUsedMemory())
        screenSaverWriter.remove(mediaItem1)
        assertEquals(30, screenSaverWriter.getUsedMemory())
        screenSaverWriter.remove(mediaItem3)
        assertEquals(0, screenSaverWriter.getUsedMemory())
    }

    @Test
    fun given_writerWithNoItems_when_removeLoadedItems_then_noItemsAreLoaded() {
        // remove loaded items
        screenSaverWriter.removeLoadedItems(null)

        // no items are loaded
        assertFalse(screenSaverWriter.hasNextItem())
    }

    @Test
    fun given_writerWithItems_when_removeAllLoadedItems_then_noItemsAreLoaded() {
        // create items and add them
        val mediaItem1 = TestMediaItem(TestScreenSaverItem())
        val mediaItem2 = TestMediaItem(TestScreenSaverItem())
        screenSaverWriter.addItem(mediaItem1)
        screenSaverWriter.addItem(mediaItem2)

        // remove all loaded items
        screenSaverWriter.removeLoadedItems(null)

        // no items are loaded
        assertFalse(screenSaverWriter.hasNextItem())
        assertTrue(mediaItem1.isDeleted)
        assertTrue(mediaItem2.isDeleted)
    }

    @Test
    fun given_writerWithMediaItems_when_removeAllLoadedItemsButFirst_then_itemRemovedButNotDeleted() {
        // create items with equal info and add them
        val item1: ScreenSaverItem = TestScreenSaverItem()
        val item2: ScreenSaverItem = TestScreenSaverItem()
        val mediaItem1 = TestMediaItem(item1)
        val mediaItem2 = TestMediaItem(item2)
        screenSaverWriter.addItem(mediaItem1)
        screenSaverWriter.addItem(mediaItem2)

        // remove all items but first
        screenSaverWriter.removeLoadedItems(mediaItem1)

        // first screen saver item has to be removed but not deleted
        assertFalse(screenSaverWriter.hasNextItem())
        assertFalse(screenSaverWriter.isItemLoaded(item1))
        assertFalse(mediaItem1.isDeleted)
        assertTrue(mediaItem2.isDeleted)
    }

    @Test
    fun given_writerWithMediaItemsWithEqualScreenSaverItem_when_removeAllLoadedItemsButFirst_then_itemRemovedButNotDeleted() {
        // create items with equal info and add them
        val item: ScreenSaverItem = TestScreenSaverItem()
        val mediaItem1 = TestMediaItem(item)
        val mediaItem2 = TestMediaItem(item)
        screenSaverWriter.addItem(mediaItem1)
        screenSaverWriter.addItem(mediaItem2)

        // remove all items but first
        screenSaverWriter.removeLoadedItems(mediaItem1)

        // screen saver item has to be loaded
        assertFalse(screenSaverWriter.hasNextItem())
        assertFalse(screenSaverWriter.isItemLoaded(item))
        assertFalse(mediaItem1.isDeleted)
    }

    @Test
    fun given_writerWithoutItems_when_removeAllOldItems_then_noItemsAreLoaded() {
        // remove all old items
        screenSaverWriter.removeOldItems(null)

        // everything is ok and no items loaded
        assertFalse(screenSaverWriter.hasNextItem())
    }

    @Test
    fun given_writerWithNewItems_when_removeAllOldItems_then_allItemsAreLoaded() {
        // create new items and add them to writer
        val items = mutableListOf<TestMediaItem>()
        for (i in 0..6) {
            val item = spy(TestMediaItem(TestScreenSaverItem(), isOld = false))
            items.add(item)
            screenSaverWriter.addItem(item)
        }

        // remove old items
        screenSaverWriter.removeOldItems(null)

        // check all items are loaded
        assertTrue(screenSaverWriter.hasNextItem())
        items.forEach {
            assertTrue(screenSaverWriter.isItemLoaded(it.screenSaverInfo))
        }
    }

    @Test
    fun given_writerWithNewItems_when_removeAllOldItemsButOne_then_allItemsAreLoaded() {
        // create new items and add them to writer
        val items = mutableListOf<TestMediaItem>()
        for (i in 0..6) {
            val item = spy(TestMediaItem(TestScreenSaverItem(), isOld = false))
            items.add(item)
            screenSaverWriter.addItem(item)
        }

        // remove all but first
        screenSaverWriter.removeOldItems(items[0])

        // check all items are loaded
        assertTrue(screenSaverWriter.hasNextItem())
        items.forEach {
            assertTrue(screenSaverWriter.isItemLoaded(it.screenSaverInfo))
        }
    }

    @Test
    fun given_writerWithOldItems_when_removeOldItems_then_noItemsAreLoaded() {
        // create old items and add them to writer
        val items = mutableListOf<TestMediaItem>()
        for (i in 0..6) {
            val item = spy(TestMediaItem(TestScreenSaverItem(), isOld = true))
            items.add(item)
            screenSaverWriter.addItem(item)
        }

        // remove all old items
        screenSaverWriter.removeOldItems(null)

        // no items are loaded
        assertFalse(screenSaverWriter.hasNextItem())
        items.forEach {
            assertFalse(screenSaverWriter.isItemLoaded(it.screenSaverInfo))
            assertTrue(it.isDeleted)
        }
    }

    @Test
    fun given_writerWithOldItems_when_removeOldItemsButOne_then_oneItemIsLoaded() {
        // create old items and add them to writer
        val items = mutableListOf<TestMediaItem>()
        for (i in 0..6) {
            val item = spy(TestMediaItem(TestScreenSaverItem(), isOld = true))
            items.add(item)
            screenSaverWriter.addItem(item)
        }

        // remove all old items
        screenSaverWriter.removeOldItems(items[0])

        // first item is loaded
        assertTrue(screenSaverWriter.hasNextItem())
        assertTrue(screenSaverWriter.isItemLoaded(items[0].screenSaverInfo))
        assertFalse(items[0].isDeleted)
    }

    @Test
    fun given_writerWithNewAndOldItems_when_removeOldItems_then_newItemsAreLoaded() {
        // create new and old items and add them to writer
        val items = mutableListOf<TestMediaItem>()
        for (i in 0..3) {
            val item = spy(TestMediaItem(TestScreenSaverItem(), isOld = true))
            items.add(item)
            screenSaverWriter.addItem(item)
        }
        for (i in 4..6) {
            val item = spy(TestMediaItem(TestScreenSaverItem(), isOld = false))
            items.add(item)
            screenSaverWriter.addItem(item)
        }

        // remove all old items
        screenSaverWriter.removeOldItems(null)

        // loaded only new items
        assertTrue(screenSaverWriter.hasNextItem())
        for (i in 0..3) {
            assertFalse(screenSaverWriter.isItemLoaded(items[i].screenSaverInfo))
            assertTrue(items[i].isDeleted)
        }
        for (i in 4..6) {
            assertTrue(screenSaverWriter.isItemLoaded(items[i].screenSaverInfo))
            assertFalse(items[i].isDeleted)
        }
    }

    @Test
    fun given_writerWithNewAndOldItems_when_removeOldItemsButOne_then_newAndOneOldItemsAreLoaded() {
        // create new and old items and add them to writer
        val items = mutableListOf<TestMediaItem>()
        for (i in 0..3) {
            val item = spy(TestMediaItem(TestScreenSaverItem(), isOld = true))
            items.add(item)
            screenSaverWriter.addItem(item)
        }
        for (i in 4..6) {
            val item = spy(TestMediaItem(TestScreenSaverItem(), isOld = false))
            items.add(item)
            screenSaverWriter.addItem(item)
        }

        // remove all old items but first
        screenSaverWriter.removeOldItems(items[0])

        // new items and first old are loaded
        assertTrue(screenSaverWriter.hasNextItem())
        assertTrue(screenSaverWriter.isItemLoaded(items[0].screenSaverInfo))
        for (i in 1..3) {
            assertFalse(screenSaverWriter.isItemLoaded(items[i].screenSaverInfo))
            assertTrue(items[i].isDeleted)
        }
        for (i in 4..6) {
            assertTrue(screenSaverWriter.isItemLoaded(items[i].screenSaverInfo))
            assertFalse(items[i].isDeleted)
        }
    }

    @Test
    fun given_writerWithMediaItems_when_removeAllLoadedItemsButFirstAndCleanItemsToDelete_then_itemDeleted() {
        // create items with equal info and add them
        val item1: ScreenSaverItem = TestScreenSaverItem()
        val item2: ScreenSaverItem = TestScreenSaverItem()
        val mediaItem1 = TestMediaItem(item1)
        val mediaItem2 = TestMediaItem(item2)
        screenSaverWriter.addItem(mediaItem1)
        screenSaverWriter.addItem(mediaItem2)

        // remove all items but first and clean items to delete
        screenSaverWriter.removeLoadedItems(mediaItem1)
        screenSaverWriter.cleanItemsToDelete(null)

        // items has to be deleted
        assertTrue(mediaItem1.isDeleted)
        assertTrue(mediaItem2.isDeleted)
    }

    @Test
    fun given_writerWithMediaItems_when_removeAllLoadedItemsButFirstAndCleanItemsToDeleteButFirst_then_itemNotDeleted() {
        // create items with equal info and add them
        val item1: ScreenSaverItem = TestScreenSaverItem()
        val item2: ScreenSaverItem = TestScreenSaverItem()
        val mediaItem1 = TestMediaItem(item1)
        val mediaItem2 = TestMediaItem(item2)
        screenSaverWriter.addItem(mediaItem1)
        screenSaverWriter.addItem(mediaItem2)

        // remove all items but first and clean items to delete
        screenSaverWriter.removeLoadedItems(mediaItem1)
        screenSaverWriter.cleanItemsToDelete(mediaItem1)

        // first items has not to be deleted
        assertFalse(mediaItem1.isDeleted)
        assertTrue(mediaItem2.isDeleted)
    }
}
