package com.yandex.tv.home.pulse

import org.hamcrest.core.IsEqual
import org.junit.Assert.assertThat
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.runners.Parameterized


@RunWith(Parameterized::class)
class FourIntegerMatchTest {

    @Parameterized.Parameter(0)
    @JvmField
    var inputValue = 0.0

    @Parameterized.Parameter(1)
    @JvmField
    var expected: List<Int> = emptyList()

    @Test
    fun `four integers match expected values`() {
        val integers = HistogramUtils.getFourIntegerApproximation(inputValue).toMutableList()
        integers.sort()

        assertThat("inputValue=$inputValue actual=${integers.joinToString()} expected=${expected.joinToString()}",
                integers, IsEqual(expected))
    }

    companion object {
        @Parameterized.Parameters
        @JvmStatic
        fun data() = listOf<Array<*>>(
                params(10.0000000001, 10, 10, 10, 10),
                params(10.10, 10, 10, 10, 10),
                params(10.24, 11, 10, 10, 10),
                params(10.25, 11, 10, 10, 10),
                params(10.35, 11, 10, 10, 10),
                params(10.45, 11, 11, 10, 10),
                params(10.55, 11, 11, 10, 10),
                params(10.65, 11, 11, 11, 10),
                params(10.75, 11, 11, 11, 10),
                params(10.80, 11, 11, 11, 10),
                params(10.85, 11, 11, 11, 10),
                params(10.90, 11, 11, 11, 11),
                params(10.99999999999, 11, 11, 11, 11)
        )

        private fun params(inputValue: Double, vararg expectedValues: Int) =
                arrayOf(inputValue, expectedValues.toMutableList().sorted())
    }
}
