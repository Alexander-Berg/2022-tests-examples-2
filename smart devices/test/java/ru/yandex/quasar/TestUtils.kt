package ru.yandex.quasar

import org.mockito.Mockito

object TestUtils {
    fun toJsonQuotes(almostJson: String): String {
        return almostJson.replace("'", "\"")
    }

    inline fun <reified T : Any> genMock() = Mockito.mock(T::class.java)
}

