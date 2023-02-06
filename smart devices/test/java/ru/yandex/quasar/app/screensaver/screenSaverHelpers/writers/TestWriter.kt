package ru.yandex.quasar.app.screensaver.screenSaverHelpers.writers

import org.mockito.kotlin.mock
import ru.yandex.quasar.app.screensaver.screenSaverMediaItems.ScreenSaverMediaItem
import java.io.InputStream

class TestWriter : ScreenSaverWriter(null) {
    override fun canLoadNewMediaItem(itemSize: Long): Boolean {
        return true
    }

    override fun restoreState() {}

    override fun save(inputStream: InputStream): ScreenSaverMediaItem {
        return mock()
    }

    override fun saveState() {}

    fun addItem(mediaItem: ScreenSaverMediaItem) {
        super.addLoadedItem(mediaItem)
    }

    fun getUsedMemory(): Long {
        return super.getUsedMemorySize()
    }
}
