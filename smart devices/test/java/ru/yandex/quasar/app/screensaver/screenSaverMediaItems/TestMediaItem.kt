package ru.yandex.quasar.app.screensaver.screenSaverMediaItems

import ru.yandex.quasar.app.screensaver.screenSaverItems.ScreenSaverItem

class TestMediaItem(
    override var screenSaverInfo: ScreenSaverItem,
    override val filePath: String? = null,
    override val size: Long = 0,
    override var creationTime: Long = 0,
    var isOld: Boolean = false
) : ScreenSaverMediaItem {

    var isDeleted: Boolean = false

    override fun isOld(updateInterval: Long, currentTime: Long): Boolean {
        return isOld
    }

    override fun delete() {
        isDeleted = true
    }
}