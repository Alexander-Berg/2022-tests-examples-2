package com.yandex.tv.common.utility.ui.tests

import com.yandex.tv.common.device.utils.BoardUtils.isHisi351
import com.yandex.tv.common.device.utils.BoardUtils.isRt28xx

enum class AppsInfo(val applicationName: String, val packageName: String) {
    ALICE_SETTINGS("Alice settings", "com.yandex.tv.alice"),
    MIRACAST_REALTEK("Дублирование экрана", "com.rtk.android.miracast"),
    MIRACAST_HISILICON("Miracast", "com.hisilicon.miracast"),
    MIRACAST_CULTRAVIEW("Wi-Fi Display Sink", "com.mediatek.androidbox"),
    KINOPOISK("Кинопоиск", "ru.kinopoisk.yandex.tv"),
    MEDIA_BROWSER_REALTEK("Медиаплеер", "com.rtk.mediabrowser"),
    MEDIA_BROWSER_HISILICON("Медиацентр", "com.cvte.tv.media"),
    MEDIA_BROWSER_CULTRAVIEW("Файловый менеджер", "com.cultraview.newfilemanager"),
    IVI("ivi", "ru.ivi.client"),
    KION("KION", "ru.mts.mtstv"),
    OKKO("Okko", "tv.okko.androidtv"),
    DEMO_APP_1("demo app 1", "yandex.egalkin.demoapp1"),
    FIRST_CHANNEL("Первый", "ru.tv1.android.tv"),
    TVIGLE("Tvigle", "ru.tvigle.tvapp"),
    MORE_TV("more.tv", "com.ctcmediagroup.videomore"),
    WINK("Wink", "ru.rt.video.app.tv"),
    YOUTUBE_PLAYER("youtube.com   ", "com.yandex.tv.ytplayer"),
    TV_LIVE("ТВ", "com.yandex.tv.live"),
    YANDEX_TV_INPUT_EFIR("", "com.yandex.tv.input.efir"),
    YANDEX_SETUPWIZARD("", "com.yandex.tv.setupwizard"),
    YANDEX_WEB_PLAYER("", "com.yandex.tv.webplayer"),
    YANDEX_SERVICES("", "com.yandex.tv.services"),
    YANDEX_UPDATER("", "com.yandex.launcher.updaterapp"),
    BUGREPORT_SENDER("", "com.yandex.tv.bugreportsender"),
    YANDEX_KEYBOARD("", "ru.yandex.androidkeyboard.tv"),
    ANDROID_TV_PROVIDERS("", "com.android.providers.tv"),
    ANDROID_SETTINGS("Settings", "com.android.tv.settings");

    companion object {

        val miracastApp: AppsInfo
            get() = when {
                isRt28xx() -> {
                    MIRACAST_REALTEK
                }
                isHisi351() -> {
                    MIRACAST_HISILICON
                }
                else -> {
                    MIRACAST_CULTRAVIEW
                }
            }

        val mediaBrowserApp: AppsInfo
            get() = when {
                isRt28xx() -> {
                    MEDIA_BROWSER_REALTEK
                }
                isHisi351() -> {
                    MEDIA_BROWSER_HISILICON
                }
                else -> {
                    MEDIA_BROWSER_CULTRAVIEW
                }
            }
    }
}
