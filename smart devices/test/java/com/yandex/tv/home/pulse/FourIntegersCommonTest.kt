package com.yandex.tv.home.pulse

import org.hamcrest.core.IsEqual
import org.junit.Assert.assertThat
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.runners.Parameterized
import java.lang.Math.abs


private const val MAX_ACCURACY_LOSS = (1 / 4.0) / 2 // four integers, assume max loss is half of distance to closest quarter boundary

@RunWith(Parameterized::class)
class FourIntegersCommonTest {

    @Parameterized.Parameter(0)
    @JvmField
    var inputValue = 0.0

    @Test
    fun `four integers accuracy loss in expected boundaries`() {
        val integers = HistogramUtils.getFourIntegerApproximation(inputValue).toMutableList()
        val average = integers.average()

        val actualLoss = abs(average - inputValue)

        assertThat("inputValue=$inputValue integers=${integers.joinToString()} actualLoss=${actualLoss} maxLoss=${MAX_ACCURACY_LOSS}",
                actualLoss <= MAX_ACCURACY_LOSS, IsEqual(true))
    }

    @Test
    fun `four integers size is four`() {
        val integers = HistogramUtils.getFourIntegerApproximation(inputValue)

        assertThat("inputValue=$inputValue integers=${integers.joinToString()} integersCount=${integers.size}",
                integers.size, IsEqual(4))
    }

    companion object {
        @Parameterized.Parameters
        @JvmStatic
        fun data() = listOf<Array<*>>(
                params(10.0000000001),
                params(10.10),
                params(10.24),
                params(10.25),
                params(10.35),
                params(10.45),
                params(10.55),
                params(10.65),
                params(10.75),
                params(10.80),
                params(10.85),
                params(10.90),
                params(10.99999999999)
        )

        private fun params(inputValue: Double) =
                arrayOf(inputValue)
    }
}
