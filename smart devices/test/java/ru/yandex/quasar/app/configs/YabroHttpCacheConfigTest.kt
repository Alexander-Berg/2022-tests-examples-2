package ru.yandex.quasar.app.configs

import org.junit.Assert
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner

@RunWith(RobolectricTestRunner::class)
class YabroHttpCacheConfigTest {
    @Test
    fun when_yabroHttpCacheIsSetButSomeFieldsAreEmpty_then_theyGetDefaultValues() {
        val httpCacheConfig = YabroHttpCacheConfig.fromConfig(mapOf())

        Assert.assertNotNull(httpCacheConfig)
        Assert.assertEquals(true, httpCacheConfig.enabled)
        Assert.assertEquals(CacheMode.DISK, httpCacheConfig.mode)
        Assert.assertEquals(20 * 1024 * 1024, httpCacheConfig.sizeBytes)
    }

    @Test
    fun when_yabroHttpCacheIsSet_then_itIsParsedCorrectly() {
        val httpCacheConfig = YabroHttpCacheConfig.fromConfig(
            mapOf("yabroHttpCache" to mapOf(
                "enabled" to false,
                "mode" to "memory",
                "sizeMb" to 10
        )))
        Assert.assertNotNull(httpCacheConfig)
        Assert.assertEquals(false, httpCacheConfig.enabled)
        Assert.assertEquals(CacheMode.MEMORY, httpCacheConfig.mode)
        Assert.assertEquals(10 * 1024 * 1024, httpCacheConfig.sizeBytes)
    }

    @Test
    fun when_sizeMbIsFloat_then_itIsParsedCorrectly() {
        val httpCacheConfig = YabroHttpCacheConfig.fromConfig(mapOf(
            "yabroHttpCache" to mapOf (
                "sizeMb" to 0.5
        )))

        Assert.assertNotNull(httpCacheConfig)
        Assert.assertEquals((0.5 * 1024 * 1024).toInt(), httpCacheConfig.sizeBytes)
    }

    @Test
    fun when_wrongTypesAreSpecified_then_exceptionIsNotThrown() {
        val httpCacheConfig = YabroHttpCacheConfig.fromConfig(mapOf(
            "yabroHttpCache" to mapOf(
                "enabled" to "true",
                "mode" to 42,
                "sizeMb" to "foo"
        )))

        Assert.assertNotNull(httpCacheConfig)
    }
}
