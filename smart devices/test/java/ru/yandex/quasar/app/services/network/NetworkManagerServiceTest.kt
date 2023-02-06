package ru.yandex.quasar.app.services.network

import android.net.NetworkInfo
import android.os.Build
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.any
import org.mockito.kotlin.mock
import org.mockito.kotlin.never
import org.mockito.kotlin.reset
import org.mockito.kotlin.verify
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import ru.yandex.quasar.fakes.FakeQuasarConnector
import ru.yandex.quasar.protobuf.ModelObjects
import ru.yandex.quasar.protobuf.ModelObjects.EthernetStatus
import ru.yandex.quasar.protobuf.ModelObjects.WifiStatus
import ru.yandex.quasar.protobuf.ModelObjects.WifiStatus.Signal
import ru.yandex.quasar.protobuf.ModelObjects.WifiStatus.Status
import ru.yandex.quasar.protobuf.QuasarProto
import ru.yandex.quasar.transport.QuasarServer


@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.M, Build.VERSION_CODES.P])
class NetworkManagerServiceTest {
    private var fakeNetworkdServer: QuasarServer = mock()
    private var fakeWifidConnector = FakeQuasarConnector()
    private var fakeEthernetController = EthernetController()
    private var networkStateHelper = NetworkStateHelper()
    private lateinit var manager: NetworkManagerService

    @Before
    fun setup() {
        manager = NetworkManagerService(WifiController(fakeWifidConnector), fakeEthernetController,
                networkStateHelper, mock(), fakeNetworkdServer)
    }

    @Test
    fun when_wifidSendsWifiStatus_then_networkdSendsItsStatusToo() {
        // Arrange
        manager.handleNetworkState(NetworkState(NetworkInterfaceType.WIFI, NetworkInfo.DetailedState.CONNECTED))

        // Act
        val wifiStatus = sendWifiStatus(Signal.EXCELLENT, Status.CONNECTED, true)

        // Assert
        val expectedNetworkStatusMessage = QuasarProto.QuasarMessage.newBuilder().setNetworkStatus(
                ModelObjects.NetworkStatus.newBuilder()
                        .setStatus(ModelObjects.NetworkStatus.Status.CONNECTED)
                        .setWifiStatus(wifiStatus)
                        .setType(ModelObjects.ConnectionType.CONNECTION_TYPE_WIFI)
        ).build()
        verify(fakeNetworkdServer).sendToAll(expectedNetworkStatusMessage)
    }

    @Test
    fun given_connectByEthernet_when_ethernetControllerSendsEthernetStatus_then_networkdSendsItsStatusToo() {
        // Arrange
        manager.handleNetworkState(NetworkState(NetworkInterfaceType.ETHERNET, NetworkInfo.DetailedState.CONNECTING))

        // Act
        sendWifiStatus(Signal.WEAK, Status.CONNECTED, true)

        // Assert
        val expectedNetworkStatusMessage = QuasarProto.QuasarMessage.newBuilder().setNetworkStatus(
                ModelObjects.NetworkStatus.newBuilder()
                        .setStatus(ModelObjects.NetworkStatus.Status.CONNECTED)
                        .setEthernetStatus(EthernetStatus.newBuilder().build())
                        .setType(ModelObjects.ConnectionType.CONNECTION_TYPE_ETHERNET)
        ).build()
        verify(fakeNetworkdServer).sendToAll(expectedNetworkStatusMessage)
    }

    @Test
    fun given_networkStateIsConnecting_when_wifiStatusIsReceived_then_networkdSendsItsStatusToo() {
        // Arrange
        manager.handleNetworkState(NetworkState(NetworkInterfaceType.ETHERNET, NetworkInfo.DetailedState.CONNECTING))

        // Act
        sendWifiStatus(Signal.WEAK, Status.CONNECTED, true)

        // Assert
        val expectedNetworkStatusMessage = QuasarProto.QuasarMessage.newBuilder().setNetworkStatus(
                ModelObjects.NetworkStatus.newBuilder()
                        .setStatus(ModelObjects.NetworkStatus.Status.CONNECTED)
                        .setEthernetStatus(EthernetStatus.newBuilder().build())
                        .setType(ModelObjects.ConnectionType.CONNECTION_TYPE_ETHERNET)
        ).build()
        verify(fakeNetworkdServer).sendToAll(expectedNetworkStatusMessage)
    }

    @Test
    fun given_connectByWifi_when_ethernetStatusUpdates_and_interfaceChangesToEthernet_then_ethernetNetworkStateIsSent() {
        // Arrange
        manager.handleNetworkState(NetworkState(NetworkInterfaceType.WIFI, NetworkInfo.DetailedState.CONNECTING))

        // Act
        sendWifiStatus(Signal.WEAK, Status.CONNECTED, true)
        reset(fakeNetworkdServer)
        manager.handleNetworkState(NetworkState(NetworkInterfaceType.ETHERNET, NetworkInfo.DetailedState.CONNECTED))

        // Assert
        val expectedNetworkStatusMessage = QuasarProto.QuasarMessage.newBuilder().setNetworkStatus(
                ModelObjects.NetworkStatus.newBuilder()
                        .setStatus(ModelObjects.NetworkStatus.Status.CONNECTED)
                        .setEthernetStatus(EthernetStatus.newBuilder().build())
                        .setType(ModelObjects.ConnectionType.CONNECTION_TYPE_ETHERNET)
        ).build()
        verify(fakeNetworkdServer).sendToAll(expectedNetworkStatusMessage)
    }

    @Test
    fun given_connectByEthernet_when_interfaceChangesToWifi_and_wifiStatusUpdates_then_wifiNetworkStateIsSent() {
        // Arrange
        manager.handleNetworkState(NetworkState(NetworkInterfaceType.ETHERNET, NetworkInfo.DetailedState.CONNECTING))

        // Act
        manager.handleNetworkState(NetworkState(NetworkInterfaceType.WIFI, NetworkInfo.DetailedState.CONNECTED))
        val wifiStatus = sendWifiStatus(Signal.EXCELLENT, Status.CONNECTED, true)

        // Assert
        val expectedNetworkStatusMessage = QuasarProto.QuasarMessage.newBuilder().setNetworkStatus(
                ModelObjects.NetworkStatus.newBuilder()
                        .setStatus(ModelObjects.NetworkStatus.Status.CONNECTED)
                        .setWifiStatus(wifiStatus)
                        .setType(ModelObjects.ConnectionType.CONNECTION_TYPE_WIFI)
        ).build()
        verify(fakeNetworkdServer).sendToAll(expectedNetworkStatusMessage)
    }

    @Test
    fun given_connectByEthernet_when_wifiStatusUpdates_and_interfaceChangesToWifi_then_wifiNetworkStateIsSent() {
        // Arrange
        manager.handleNetworkState(NetworkState(NetworkInterfaceType.ETHERNET, NetworkInfo.DetailedState.CONNECTING))

        // Act
        val wifiStatus = sendWifiStatus(Signal.EXCELLENT, Status.CONNECTED, true)
        manager.handleNetworkState(NetworkState(NetworkInterfaceType.WIFI, NetworkInfo.DetailedState.CONNECTED))

        // Assert
        val expectedNetworkStatusMessage = QuasarProto.QuasarMessage.newBuilder().setNetworkStatus(
                ModelObjects.NetworkStatus.newBuilder()
                        .setStatus(ModelObjects.NetworkStatus.Status.CONNECTED)
                        .setWifiStatus(wifiStatus)
                        .setType(ModelObjects.ConnectionType.CONNECTION_TYPE_WIFI)
        ).build()
        verify(fakeNetworkdServer).sendToAll(expectedNetworkStatusMessage)
    }

    @Test
    fun when_resetNetwork_then_correspondingControllerIsCalled() {
        // Arrange
        val ethernetController: EthernetController = mock()
        val wifiController: WifiController = mock()
        manager = NetworkManagerService(wifiController, ethernetController,
                networkStateHelper, mock(), fakeNetworkdServer)
        manager.handleNetworkState(NetworkState(NetworkInterfaceType.ETHERNET, NetworkInfo.DetailedState.CONNECTED))

        // Act
        manager.handleQuasarMessage(QuasarProto.QuasarMessage.newBuilder().setResetNetwork(ModelObjects.EmptyMessage.getDefaultInstance()).build(), mock())

        // Assert
        verify(ethernetController).resetNetwork(any(), any())
        verify(wifiController, never()).resetNetwork(any(), any())

        /* Now we check that controller is switched when the interface is switched */

        // Arrange
        reset(ethernetController)
        reset(wifiController)
        manager.handleNetworkState(NetworkState(NetworkInterfaceType.WIFI, NetworkInfo.DetailedState.CONNECTED))

        // Act
        manager.handleQuasarMessage(QuasarProto.QuasarMessage.newBuilder().setResetNetwork(ModelObjects.EmptyMessage.getDefaultInstance()).build(), mock())

        // Assert
        verify(wifiController).resetNetwork(any(), any())
        verify(ethernetController, never()).resetNetwork(any(), any())
    }

    private fun sendWifiStatus(signal: Signal, status: Status, internetReachable: Boolean): WifiStatus? {
        val wifiStatus = WifiStatus.newBuilder()
                .setInternetReachable(internetReachable)
                .setSignal(signal)
                .setStatus(status).build()
        fakeWifidConnector.receiveQuasarMessage(
                QuasarProto.QuasarMessage.newBuilder().setWifiStatus(wifiStatus).build()
        )
        return wifiStatus
    }
}
