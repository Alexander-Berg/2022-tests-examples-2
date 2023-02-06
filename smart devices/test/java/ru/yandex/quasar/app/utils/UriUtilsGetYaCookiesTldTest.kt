package ru.yandex.quasar.app.utils

import android.net.Uri
import org.junit.Assert
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.ParameterizedRobolectricTestRunner

@RunWith(ParameterizedRobolectricTestRunner::class)
class UriUtilsGetYaCookiesTldTest(private val uri: String, private val expectedTld: String?) {

    @Test
    fun test() {
        Assert.assertEquals(expectedTld, UriUtils.getYaCookieTld(Uri.parse(uri)))
    }

    companion object {
        @JvmStatic
        @Suppress("unused")
        @ParameterizedRobolectricTestRunner.Parameters(name = "{0} - {1}")
        fun getParameters(): List<Array<out Any?>> {
            return listOf(
                // simple case
                "https://yandex.ru" to "ru",
                "https://yandex.ru." to "ru",
                "https://yandex.com" to "com",
                "https://yandex.ua" to "ua",
                "https://yandex.by" to "by",
                "https://yandex.kz" to "kz",
                "https://yandex.az" to "az",

                // more complex hostname
                "https://complex-hostname.something.yandex.ru" to "ru",
                "https://complex-hostname.something.yandex.com" to "com",
                "https://complex-hostname.something.yandex.com." to "com",

                // TLD only
                "https://com" to "com",
                "https://com." to "com",

                // compound TLDs
                "https://yandex.co.il" to null,
                "https://yandex.com.am" to null,
                "https://yandex.com.ge" to null,
                "https://yandex.com.tr" to "com.tr",

                // compound TLDs only
                "https://co.il" to null,
                "https://com.am" to null,
                "https://com.ge" to null,
                "https://com.tr" to "com.tr",

                // compound TLDs with dot
                "https://yandex.co.il." to null,
                "https://yandex.com.am." to null,
                "https://yandex.com.ge." to null,
                "https://yandex.com.tr." to "com.tr"

            ).map { arrayOf(it.first, it.second) }
        }
    }
}