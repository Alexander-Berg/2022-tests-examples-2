package ru.yandex.quasar.fakes

import android.content.Context
import android.net.NetworkInfo
import ru.yandex.quasar.core.Configuration
import ru.yandex.quasar.app.common.network.ConnectionProber
import ru.yandex.quasar.app.services.wifi.ConnectivityChecker
import ru.yandex.quasar.app.services.wifi.WifiConnectionState
import ru.yandex.quasar.app.services.wifi.WifiStateHelper
import ru.yandex.quasar.metrica.MetricaConnector
import ru.yandex.quasar.protobuf.ModelObjects
import ru.yandex.quasar.transport.QuasarServer
import java.util.concurrent.ScheduledExecutorService

class ConnectivityCheckerFake(configuration: Configuration,
                              workerExecutor: ScheduledExecutorService,
                              context: Context,
                              metricaConnector: MetricaConnector,
                              connectionProber: ConnectionProber,
                              wifiStateHelper: WifiStateHelper,
                              server: QuasarServer)
    : ConnectivityChecker(
        configuration,
        workerExecutor,
        context,
        metricaConnector,
        connectionProber,
        wifiStateHelper,
        server) {
    fun setState(internetReachable: Boolean,
                 connectivityState: NetworkInfo.DetailedState,
                 wifiStatus: ModelObjects.WifiStatus.Status,
                 signalStatus: ModelObjects.WifiStatus.Signal) {
        this.internetReachable = internetReachable
        this.connectivityState = connectivityState
        this.wifiState = WifiConnectionState(wifiStatus, signalStatus)
    }
}
