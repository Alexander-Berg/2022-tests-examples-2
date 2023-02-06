package com.yandex.tv.home.pulse

import org.hamcrest.core.IsEqual
import org.junit.Assert.assertThat
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.runners.Parameterized


@RunWith(Parameterized::class)
class FourIntegerCeilingAndFloorTest {

    @Parameterized.Parameter(0)
    @JvmField
    var inputValue = 0.0

    @Parameterized.Parameter(1)
    @JvmField
    var floor = 0

    @Parameterized.Parameter(2)
    @JvmField
    var ceiling = 0

    @Test
    fun `four integers are either floor or ceiling of original value`() {
        val integers = HistogramUtils.getFourIntegerApproximation(inputValue)

        val isFloorOrCeiling = integers.none { it != floor && it != ceiling }
        assertThat("floor=$floor ceiling=$ceiling integers=${integers.joinToString()}", isFloorOrCeiling, IsEqual(true))
    }

    companion object {
        @Parameterized.Parameters
        @JvmStatic
        fun data() = listOf<Array<*>>(
                params(10.3, 10, 11),
                params(10.1, 10, 11),
                params(10.1, 10, 11),
                params(10.0001, 10, 11),
                params(10.6, 10, 11),
                params(9.99, 9, 10)
        )

        private fun params(inputValue: Double, floor: Int, ceiling: Int) =
                arrayOf(inputValue, floor, ceiling)
    }
}
