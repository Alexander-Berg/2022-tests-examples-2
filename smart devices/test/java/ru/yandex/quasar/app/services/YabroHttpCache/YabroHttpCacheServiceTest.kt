package ru.yandex.quasar.app.services.YabroHttpCache

import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.*
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.app.configs.CacheMode
import ru.yandex.quasar.app.configs.SystemConfig
import ru.yandex.quasar.app.configs.YabroHttpCacheConfig
import ru.yandex.quasar.app.services.SuicideService
import ru.yandex.quasar.app.webview.yabro.YabroHttpCacheService
import ru.yandex.quasar.app.webview.yabro.YabroViewEarlySetup
import ru.yandex.quasar.fakes.ExternalConfigObservableFake

@RunWith(RobolectricTestRunner::class)
class YabroHttpCacheServiceTest {

    private val configObserver = ExternalConfigObservableFake()
    private val yabroEarlySetup: YabroViewEarlySetup = mock()
    private val suicideService: SuicideService = mock()

    @Test
    fun given_configExistsOnStart_when_serviceStarts_then_appDoesntRestart() {
        // Arrange
        val httpCacheConfig = YabroHttpCacheConfig()
        val systemConfig: SystemConfig = mock()
        whenever(systemConfig.yabroHttpCacheConfig).thenReturn(httpCacheConfig)
        configObserver.receiveSystemConfig(systemConfig)

        // Act
        YabroHttpCacheService(configObserver, suicideService, yabroEarlySetup)

        // Assert
        verify(suicideService, never()).killSelf(any())
    }

    @Test
    fun given_configExistsOnStart_when_newConfigIsReceived_then_appRestart() {
        // Arrange
        val httpCacheConfig = YabroHttpCacheConfig(true, CacheMode.MEMORY, 10.0)
        val systemConfig: SystemConfig = mock()
        whenever(systemConfig.yabroHttpCacheConfig).thenReturn(httpCacheConfig)
        configObserver.receiveSystemConfig(systemConfig)

        val service = YabroHttpCacheService(configObserver, suicideService, yabroEarlySetup)
        service.start(httpCacheConfig)

        // Act
        val newHttpCacheConfig = YabroHttpCacheConfig(true, CacheMode.DISK, 20.0)
        val newSystemConfig: SystemConfig = mock()
        whenever(newSystemConfig.yabroHttpCacheConfig).thenReturn(newHttpCacheConfig)
        configObserver.receiveSystemConfig(newSystemConfig)

        // Assert
        verify(suicideService).killSelf(0)
    }

    @Test
    fun given_configExistsOnStart_when_sameConfigIsReceived_then_appDoesntRestart() {
        // Arrange
        val httpCacheConfig = YabroHttpCacheConfig()
        val systemConfig: SystemConfig = mock()
        whenever(systemConfig.yabroHttpCacheConfig).thenReturn(httpCacheConfig)
        configObserver.receiveSystemConfig(systemConfig)

        YabroHttpCacheService(configObserver, suicideService, yabroEarlySetup)

        // Act
        val newHttpCacheConfig = YabroHttpCacheConfig()
        val newSystemConfig: SystemConfig = mock()
        whenever(newSystemConfig.yabroHttpCacheConfig).thenReturn(newHttpCacheConfig)
        configObserver.receiveSystemConfig(newSystemConfig)

        // Assert
        verify(suicideService, never()).killSelf(any())
    }

    @Test
    fun given_configExistsOnStart_when_serviceIsStarted_then_yabroSetupIsDone() {
        // Arrange
        val httpCacheConfig = YabroHttpCacheConfig(false, CacheMode.MEMORY, 10.0)
        val systemConfig: SystemConfig = mock()
        whenever(systemConfig.yabroHttpCacheConfig).thenReturn(httpCacheConfig)
        configObserver.receiveSystemConfig(systemConfig)

        // When
        val service = YabroHttpCacheService(configObserver, suicideService, yabroEarlySetup)
        service.start(httpCacheConfig)


        // Assert
        verify(yabroEarlySetup).disableHttpCache()
        verify(yabroEarlySetup).setInMemoryHttpCache()
        verify(yabroEarlySetup).setHttpCacheSize(10 * 1024 * 1024)
    }

    @Test
    fun given_configExistsOnStart_when_configDoesntDisableCache_then_cacheIsNotDisabled() {
        // Arrange
        val oldHttpCacheConfig = YabroHttpCacheConfig(true)
        val oldSystemConfig: SystemConfig = mock()
        whenever(oldSystemConfig.yabroHttpCacheConfig).thenReturn(oldHttpCacheConfig)
        configObserver.receiveSystemConfig(oldSystemConfig)

        // When
        YabroHttpCacheService(configObserver, suicideService, yabroEarlySetup)

        // Assert
        verify(yabroEarlySetup, never()).disableHttpCache()
    }

    @Test
    fun given_configExistsOnStart_when_configDoesntSetInMemoryCache_then_inMemoryCacheIsNotSetup() {
        // Arrange
        val oldHttpCacheConfig = YabroHttpCacheConfig(true, CacheMode.DISK, 20.0)
        val oldSystemConfig: SystemConfig = mock()
        whenever(oldSystemConfig.yabroHttpCacheConfig).thenReturn(oldHttpCacheConfig)
        configObserver.receiveSystemConfig(oldSystemConfig)

        // When
        YabroHttpCacheService(configObserver, suicideService, yabroEarlySetup)

        // Assert
        verify(yabroEarlySetup, never()).setInMemoryHttpCache()
    }
}
