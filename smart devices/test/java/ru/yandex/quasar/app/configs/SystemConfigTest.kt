package ru.yandex.quasar.app.configs

import androidx.annotation.NonNull
import com.fasterxml.jackson.databind.ObjectMapper
import org.junit.Assert
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.mock
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.TestUtils

@RunWith(RobolectricTestRunner::class)
class SystemConfigTest {
    @NonNull
    private val objectMapper = ObjectMapper()

    @Test
    fun when_yabroHttpCacheIsNotSet_then_fieldIsNotNull() {
        val json = TestUtils.toJsonQuotes("{}")
        val map = objectMapper.readValue(json, Map::class.java)
        val systemConfig = SystemConfig(map as MutableMap<String, Any>?, mock())
        val httpCacheConfig = systemConfig.yabroHttpCacheConfig

        Assert.assertNotNull(httpCacheConfig)
    }

    @Test
    fun when_yabroHttpCacheIsSet_then_fieldIsNotNull() {
        val json = TestUtils.toJsonQuotes("{'yabroHttpCache': {}}")
        val map = objectMapper.readValue(json, Map::class.java)
        val systemConfig = SystemConfig(map as MutableMap<String, Any>?, mock())
        val httpCacheConfig = systemConfig.yabroHttpCacheConfig

        Assert.assertNotNull(httpCacheConfig)
    }
}
