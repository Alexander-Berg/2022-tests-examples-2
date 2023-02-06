package ru.yandex.quasar.fakes

import org.mockito.kotlin.mock
import org.mockito.kotlin.whenever
import ru.yandex.quasar.app.configs.ExternalConfigObservable
import ru.yandex.quasar.app.configs.StationConfig
import ru.yandex.quasar.app.configs.SystemConfig

class ExternalConfigObservableFake : ExternalConfigObservable() {
    val stationConfig: StationConfig = mock()

    fun receiveSystemConfig(systemConfig: SystemConfig) {
        whenever(stationConfig.systemConfig).thenReturn(systemConfig)
        this.receiveValue(stationConfig)
    }
}
