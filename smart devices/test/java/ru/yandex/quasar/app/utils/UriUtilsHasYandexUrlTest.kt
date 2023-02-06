package ru.yandex.quasar.app.utils

import android.net.Uri
import org.junit.Assert
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.ParameterizedRobolectricTestRunner

@RunWith(ParameterizedRobolectricTestRunner::class)
class UriUtilsIsYandexHost(private val uri: String, private val expectedResult: Boolean) {

    @Test
    fun test() {
        Assert.assertEquals(expectedResult,  UriUtils.hasYandexHost(Uri.parse(uri)))
    }

    companion object {
        @JvmStatic
        @Suppress("unused")
        @ParameterizedRobolectricTestRunner.Parameters(name = "{0} - {1}")
        fun getParameters(): List<Array<out Any?>> {
            return listOf(
                // simple case
                "https://yandex.ru" to true,
                "https://yandex.ru." to true,    // https://tools.ietf.org/html/rfc1035

                // should allow any path
                "https://yandex.ru/something" to true,

                // and query too
                "https://yandex.ru?param1=1&param2=2" to true,

                // able to browse any 3rd level domain
                "https://something.yandex.ru/" to true,
                "https://CAPS.yandex.ru/" to true,
                "https://123456789.yandex.ru/" to true,
                "https://---.yandex.ru/" to true,

                // and Nth level domain too
                "https://host1.host2.host3.yandex.ru/" to true,

                // any other scheme should be allowed
                "http://yandex.ru" to true,
                "ftp://yandex.ru" to true,

                // check list of other allowed top level domains
                "https://yandex.by" to true,
                "https://yandex.ua" to true,
                "https://yandex.kz" to true,
                "https://yandex.com" to true,
                "https://yandex.com.tr" to true,
                "https://yandex.az" to true,
                "https://yandex.net" to false,
                "https://quasar.s3.yandex.net" to true,

                // check for ya.ru
                "https://ya.ru" to true,
                "https://ya.ru." to true,
                "https://www.ya.ru" to true,

                // but
                "https://other.ya.ru" to false,
                "https://ya.com" to false,

                // those domains are not allowed
                "https://google.com" to false,
                "https://yandex.asdf" to false,
                "https://neyandex.ru" to false,
                "https://yandex.hax.ru" to false,
                "https://yandex.ru.hostile.host.ru" to false

            ).map { arrayOf(it.first, it.second) }
        }
    }
}