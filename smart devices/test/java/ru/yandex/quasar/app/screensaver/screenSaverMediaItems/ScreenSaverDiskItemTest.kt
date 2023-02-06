package ru.yandex.quasar.app.screensaver.screenSaverMediaItems

import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.mockito.kotlin.mock
import org.mockito.kotlin.whenever
import java.io.File

class ScreenSaverDiskItemTest {
    private val file: File = mock()

    @Before
    fun setUp() {
        whenever(file.path).thenReturn("path1")
        whenever(file.lastModified()).thenReturn(100)
        whenever(file.length()).thenReturn(10)
    }

    @Test
    fun given_file_when_createDiskItem_then_successCreation() {
        val diskItem = ScreenSaverDiskItem(file)
        assertEquals(file.path, diskItem.filePath)
        assertEquals(file.lastModified(), diskItem.creationTime)
        assertEquals(file.length(), diskItem.size)
    }

    @Test
    fun given_diskItem_when_isOld_then_resultIsCorrect() {
        val diskItem = ScreenSaverDiskItem(file)
        assertEquals(file.path, diskItem.filePath)
        assertEquals(file.lastModified(), diskItem.creationTime)
        assertEquals(file.length(), diskItem.size)

        assertTrue(diskItem.isOld(0, 101))
        assertFalse(diskItem.isOld(0, 100))

        assertTrue(diskItem.isOld(10, 200))
        assertTrue(diskItem.isOld(10, 111))

        assertFalse(diskItem.isOld(10, 110))
        assertFalse(diskItem.isOld(10, 105))
        assertFalse(diskItem.isOld(10, 100))
        assertFalse(diskItem.isOld(10, 90))
        assertFalse(diskItem.isOld(10, -90))

        assertTrue(diskItem.isOld(-10, 100))
        assertFalse(diskItem.isOld(-10, -100))
        assertFalse(diskItem.isOld(-10, 90))
    }

    @Test
    fun given_twoDiskItemsWithTheSameFile_when_compare_then_equals() {
        // create copy of original file
        val fileCopy: File = mock()
        val filePath = file.path
        whenever(fileCopy.path).thenReturn(filePath)
        val lastModified = file.lastModified()
        whenever(fileCopy.lastModified()).thenReturn(lastModified)
        val fileSize = file.length()
        whenever(fileCopy.length()).thenReturn(fileSize)

        // create two disk items with same file
        val diskItem: ScreenSaverMediaItem = ScreenSaverDiskItem(file)
        val diskItemCopy: ScreenSaverMediaItem = ScreenSaverDiskItem(fileCopy)

        // items have to be equal
        assertEquals(diskItem, diskItemCopy)
    }

    @Test
    fun given_twoDiskItems_when_compare_then_notEquals() {
        // create second file
        val file2: File = mock()
        whenever(file2.path).thenReturn("path2")
        whenever(file2.lastModified()).thenReturn(200)
        whenever(file2.length()).thenReturn(20)

        // create two disk items with different files
        val diskItem: ScreenSaverMediaItem = ScreenSaverDiskItem(file)
        val diskItem2: ScreenSaverMediaItem = ScreenSaverDiskItem(file2)

        // items have to be not equal
        assertNotEquals(diskItem, diskItem2)
    }

    @Test
    fun given_diskItemAndTestMediaItem_when_compare_then_notEquals() {
        // create disk item and test media item
        val diskItem: ScreenSaverMediaItem = ScreenSaverDiskItem(file)
        val notDiskItem: ScreenSaverMediaItem = TestMediaItem(mock(), "path1", 10)

        // items have to be not equal
        assertNotEquals(diskItem, notDiskItem)
    }
}
