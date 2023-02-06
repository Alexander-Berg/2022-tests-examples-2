package ru.yandex.quasar.app.screensaver.screenSaverItems

class TestScreenSaverItem(private val url: String? = null) : ScreenSaverItem {
    override fun getUrl(): String? {
        return url
    }

    override fun isValid(): Boolean {
        return false
    }
}
