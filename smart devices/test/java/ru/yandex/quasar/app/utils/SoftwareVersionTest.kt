package ru.yandex.quasar.app.utils

import org.assertj.core.api.Assertions
import org.junit.Test
import java.lang.NumberFormatException

class SoftwareVersionTest {
    private fun v(s: String) = SoftwareVersion.parse(s)

    @Test
    fun compareTo_shouldSortLexicographically_ifSameLength() {
        Assertions.assertThat(v("2.2.0")).isLessThan(v("2.2.1"))
        Assertions.assertThat(v("2.2.9")).isLessThan(v("2.2.10"))
        Assertions.assertThat(v("2.3.9")).isLessThan(v("2.4.0"))
        Assertions.assertThat(v("1.0")).isLessThan(v("2.0"))
        Assertions.assertThat(v("1.0")).isLessThan(v("02.0"))
        Assertions.assertThat(v("0")).isLessThan(v("1"))
        Assertions.assertThat(v("9")).isLessThan(v("10"))
    }

    @Test
    fun compareTo_shouldSortLexicographically_ifDifferentLength() {
        Assertions.assertThat(v("2")).isLessThan(v("2.1"))
        Assertions.assertThat(v("2.2")).isLessThan(v("2.2.1"))
        Assertions.assertThat(v("2.2.2")).isLessThan(v("2.3"))
    }

    @Test
    fun parse_shouldThrowNumberFormatException_ifInvalidFormat() {
        Assertions.assertThatThrownBy { SoftwareVersion.parse("1.2.3.ENG") }
            .isInstanceOf(NumberFormatException::class.java)
    }

    @Test
    fun parse_shouldTakeOnlyFiveFirstParts_ifVersionIsTooLong() {
        Assertions.assertThat(SoftwareVersion.parse("1.2.3.4.5.6.7.8"))
            .isEqualToComparingFieldByField(SoftwareVersion.parse("1.2.3.4.5"))
    }
}