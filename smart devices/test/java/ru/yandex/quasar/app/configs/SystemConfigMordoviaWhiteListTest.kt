package ru.yandex.quasar.app.configs

import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import org.assertj.core.api.Assertions
import org.junit.Assert
import org.junit.Test

class SystemConfigMordoviaWhiteListTest {
    private val gson = Gson()

    @Test
    fun mordoviaWhitList_shouldBeParsedCorrectly() {
        val jsonConfig = gson.fromJson<Map<String, Any>>(
            "{\"mordoviaWhiteList\": [" +
                    "null, " +
                    "1, " +
                    "{}, " +
                    "{\"a\": \"a\", \"b\": 1}, " +
                    "true, " +
                    "\"*BADPATT\$RN\", " +
                    "\"^https?://(www.)?google.com/?.*\$\"" +
                    "]}",
            object : TypeToken<Map<String, Any>>() {}.type
        )

        val patterns = SystemConfig.parseListOfPatterns(jsonConfig["mordoviaWhiteList"] as List<*>)
        Assertions.assertThat(patterns).hasSize(1)

        val pattern = patterns[0]
        Assert.assertTrue(pattern.matcher("https://google.com").matches())
        Assert.assertTrue(pattern.matcher("http://www.google.com").matches())
    }

}