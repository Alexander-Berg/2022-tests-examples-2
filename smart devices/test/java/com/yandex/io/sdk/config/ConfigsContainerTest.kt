package com.yandex.io.sdk.config

import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.aMapWithSize
import org.hamcrest.Matchers.hasEntry
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner

@RunWith(RobolectricTestRunner::class)
class ConfigsContainerTest {

    @Test
    fun `ofNamesWithValues() make valid container`() {
        val actual = ConfigsContainer.ofNamesWithValues(arrayOf(CONFIG_KEY_1, CONFIG_KEY_2, CONFIG_KEY_NULL)) {
            when (it) {
                CONFIG_KEY_1 -> CONFIG_VALUE_1
                CONFIG_KEY_2 -> CONFIG_VALUE_2
                else -> null
            }
        }

        assertThat(actual.configs, aMapWithSize(2))
        assertThat(actual.configs, hasEntry(CONFIG_KEY_1, CONFIG_VALUE_1))
        assertThat(actual.configs, hasEntry(CONFIG_KEY_2, CONFIG_VALUE_2))
    }

    private companion object {
        const val CONFIG_KEY_1 = "key_1"
        const val CONFIG_KEY_2 = "key_2"
        const val CONFIG_KEY_NULL = "key_null"
        const val CONFIG_VALUE_1 = "{\"test_key\":123}"
        const val CONFIG_VALUE_2 = "{\"test_key\":234}"
    }
}
