package ru.yandex.quasar.app.services.wifi

import android.content.Context
import android.content.Intent
import android.net.ConnectivityManager
import android.net.NetworkInfo
import android.net.NetworkInfo.DetailedState
import android.net.wifi.SupplicantState
import android.net.wifi.WifiManager
import android.os.Build
import android.os.Parcelable
import androidx.test.core.app.ApplicationProvider
import org.junit.Assert
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.ArgumentMatchers.anyString
import org.mockito.kotlin.any
import org.mockito.kotlin.eq
import org.mockito.kotlin.inOrder
import org.mockito.kotlin.mock
import org.mockito.kotlin.never
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import org.robolectric.Shadows.shadowOf
import org.robolectric.annotation.Config
import org.robolectric.shadow.api.Shadow
import org.robolectric.shadows.ShadowNetworkInfo
import org.robolectric.shadows.ShadowWifiManager
import ru.yandex.quasar.app.common.network.ConnectionProber
import ru.yandex.quasar.fakes.ConnectivityCheckerFake
import ru.yandex.quasar.metrica.MetricaConnector
import ru.yandex.quasar.protobuf.ModelObjects
import ru.yandex.quasar.protobuf.ModelObjects.WifiStatus.Signal
import ru.yandex.quasar.protobuf.ModelObjects.WifiStatus.Status
import ru.yandex.quasar.protobuf.QuasarProto
import ru.yandex.quasar.transport.QuasarServer
import java.util.concurrent.ScheduledExecutorService
import java.util.concurrent.TimeUnit

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.M, Build.VERSION_CODES.P])
class ConnectivityCheckerTest {

    private lateinit var connectivityChecker: ConnectivityCheckerFake
    private val wifidServer: QuasarServer = mock()
    private val prober: ConnectionProber = mock()
    private val executor: ScheduledExecutorService = mock()
    private val connector: MetricaConnector = mock()
    private val wifiStateHelper = WifiStateHelper()
    private val context = ApplicationProvider.getApplicationContext<Context>()
    private val wifiManager = context.getSystemService(Context.WIFI_SERVICE) as WifiManager

    @Before
    fun setUp() {
        context
        connectivityChecker = ConnectivityCheckerFake(
                mock(),
                executor,
                context,
                connector,
                prober,
                wifiStateHelper,
                wifidServer)
        setBSSID("de:ad:be:ef:01:23")
    }

    fun setBSSID(bssid: String) {
        shadowOf(wifiManager.connectionInfo).setBSSID(bssid)
    }

    fun createWifiInfo(signalLevel: Int, channel: Int, frequency: Int, ssid: String): ModelObjects.WifiInfo {
        return ModelObjects.WifiInfo.newBuilder()
                .setRssi(signalLevel)
                .setSecure(true)
                .setChannel(channel)
                .setFreq(frequency)
                .setSsid(ssid)
                .build()
    }

    fun createWifiStatusMessage(wifiStatus: Status,
                                signalStatus: Signal,
                                internetReachable: Boolean
    ): QuasarProto.QuasarMessage {
        return QuasarProto.QuasarMessage.newBuilder().setWifiStatus(
                ModelObjects.WifiStatus.newBuilder()
                        .setStatus(wifiStatus)
                        .setSignal(signalStatus)
                        .setInternetReachable(internetReachable)
                        .setCurrentNetwork(
                            ModelObjects.WifiInfo.newBuilder()
                                .setSsid(wifiStateHelper.removeQuotes(wifiManager.connectionInfo.ssid))
                                .setMac(wifiStateHelper.getBSSID(wifiManager.connectionInfo))
                                .setFreq(wifiManager.connectionInfo.frequency)
                                .setChannel(wifiStateHelper.getChannel(wifiManager.connectionInfo.frequency))
                                .build()
                        )
                        .build()
        ).build()
    }

    @Test
    fun given_wifiStatusWasSentToMetricaOnce_when_updateContainsSameStatus_then_itIsNotSentToMetrica() {
        // Arrange
        connectivityChecker.setState(true, DetailedState.CONNECTED, Status.CONNECTED, Signal.WEAK)

        // Act
        whenever(prober.checkConnectivity()).thenReturn(true)
        ShadowWifiManager.setSignalLevelInPercent(0F)
        connectivityChecker.checkConnection()

        // Assert
        verify(wifidServer, never()).sendToAll(any())
    }

    @Test
    fun when_connectivityDisappears_then_properStatusIsSent() {
        // Arrange
        connectivityChecker.setState(true, DetailedState.CONNECTED, Status.CONNECTED, Signal.EXCELLENT)

        // Act
        whenever(prober.checkConnectivity()).thenReturn(false)
        ShadowWifiManager.setSignalLevelInPercent(0F)
        connectivityChecker.checkConnection()

        // Assert
        val expectedWifiStatus = createWifiStatusMessage(Status.CONNECTED_NO_INTERNET, Signal.WEAK, false)
        verify(wifidServer).sendToAll(expectedWifiStatus)
    }

    @Test
    fun when_connectivityAppears_then_properStatusIsSent() {
        // Arrange
        connectivityChecker.setState(false, DetailedState.DISCONNECTED, Status.NOT_CONNECTED, Signal.WEAK)

        // Act
        whenever(prober.checkConnectivity()).thenReturn(true)
        ShadowWifiManager.setSignalLevelInPercent(1F)
        connectivityChecker.checkConnection()

        // Assert
        val expectedWifiStatus = createWifiStatusMessage(Status.CONNECTED, Signal.EXCELLENT, true)
        verify(wifidServer).sendToAll(expectedWifiStatus)
    }

    @Test
    fun given_firstConnectivityCheck_when_run_then_schedulesNextProbeInDefaultDelay() {
        // Arrange
        whenever(prober.checkConnectivity()).thenReturn(true)

        // Act
        connectivityChecker.checkConnection()

        // Assert
        verify(executor).schedule(any(), eq(ConnectivityChecker.DEFAULT_DELAY_MSEC), eq(TimeUnit.MILLISECONDS))
    }

    @Test
    fun given_connectionDisappears_when_connectionDisappears_then_schedulesNextProbeWithAscendingDelays() {
        // Arrange
        connectivityChecker.setState(true, DetailedState.CONNECTED, Status.CONNECTED, Signal.EXCELLENT)

        // Act
        whenever(prober.checkConnectivity()).thenReturn(false)
        connectivityChecker.checkConnection()
        connectivityChecker.checkConnection()
        connectivityChecker.checkConnection()
        connectivityChecker.checkConnection()
        connectivityChecker.checkConnection()

        // Assert
        inOrder(executor) {
            verify(executor).schedule(any(), eq(ConnectivityChecker.FAST_RETRY_DELAY_MSEC), eq(TimeUnit.MILLISECONDS))
            verify(executor).schedule(any(), eq(ConnectivityChecker.FAST_RETRY_DELAY_MSEC * 2), eq(TimeUnit.MILLISECONDS))
            verify(executor).schedule(any(), eq(ConnectivityChecker.FAST_RETRY_DELAY_MSEC * 4), eq(TimeUnit.MILLISECONDS))
            verify(executor).schedule(any(), eq(ConnectivityChecker.FAST_RETRY_DELAY_MSEC * 8), eq(TimeUnit.MILLISECONDS))
            verify(executor).schedule(any(), eq(ConnectivityChecker.DEFAULT_DELAY_MSEC), eq(TimeUnit.MILLISECONDS))
        }
    }

    @Test
    fun given_noInternet_when_internetAppears_then_wifiConnectEventIsReported() {
        // Arrange
        connectivityChecker.setState(false, DetailedState.DISCONNECTED, Status.NOT_CONNECTED, Signal.WEAK)

        // Act
        whenever(prober.checkConnectivity()).thenReturn(true)
        ShadowWifiManager.setSignalLevelInPercent(1F)
        connectivityChecker.checkConnection()

        // Assert
        verify(connector).reportEvent(eq("wifiConnect"), anyString())
    }

    @Test
    fun given_internetExists_when_internetDisappears_then_wifiDisconnectEventIsReported() {
        // Arrange
        connectivityChecker.setState(true, DetailedState.CONNECTED, Status.CONNECTED, Signal.GOOD)

        // Act
        whenever(prober.checkConnectivity()).thenReturn(false)
        ShadowWifiManager.setSignalLevelInPercent(0F)
        connectivityChecker.checkConnection()

        // Assert
        verify(connector).reportEvent(eq("wifiDisconnect"), anyString())
    }

    @Test
    fun given_supplicantIsDisconnectedWithAuthenticationError_when_onNetworkStateChangeReceive_then_supplicantAuthErrorIsSet() {
        // Arrange
        val intent = Intent(WifiManager.SUPPLICANT_STATE_CHANGED_ACTION)
        val supplicantState = SupplicantState.DISCONNECTED
        intent.putExtra(WifiManager.EXTRA_NEW_STATE, supplicantState as Parcelable)
        intent.putExtra(WifiManager.EXTRA_SUPPLICANT_ERROR, WifiManager.ERROR_AUTHENTICATING)

        // Act
        connectivityChecker.onNetworkStateChangeReceive(intent)

        // Assert
        Assert.assertEquals(true, connectivityChecker.supplicantAuthError)
    }

    @Test
    fun when_networkStateChangedIntentReceived_then_properWifiStatusIsSent() {
        // Arrange
        connectivityChecker.setState(false,
                DetailedState.DISCONNECTED,
                Status.NOT_CONNECTED,
                Signal.EXCELLENT)

        val intent = Intent(WifiManager.NETWORK_STATE_CHANGED_ACTION)
        val networkInfo = Shadow.newInstanceOf<NetworkInfo>(NetworkInfo::class.java)
        val shadowNetworkInfo = Shadow.extract<ShadowNetworkInfo>(networkInfo)
        shadowNetworkInfo.setDetailedState(DetailedState.CONNECTED)
        intent.putExtra(WifiManager.EXTRA_NETWORK_INFO, networkInfo)

        // Act
        connectivityChecker.onNetworkStateChangeReceive(intent)

        // Assert
        val expectedWifiStatus = createWifiStatusMessage(Status.CONNECTED_NO_INTERNET, Signal.EXCELLENT, false)
        verify(wifidServer).sendToAll(expectedWifiStatus)
    }

    @Test
    fun when_networkStateChangedIntentReceived_then_properWifiStatusIsSent_2() {
        // Arrange
        connectivityChecker.setState(false,
                DetailedState.CONNECTED,
                Status.CONNECTED,
                Signal.GOOD)

        val intent = Intent(WifiManager.NETWORK_STATE_CHANGED_ACTION)
        val networkInfo = Shadow.newInstanceOf<NetworkInfo>(NetworkInfo::class.java)
        val shadowNetworkInfo = Shadow.extract<ShadowNetworkInfo>(networkInfo)
        shadowNetworkInfo.setDetailedState(DetailedState.CAPTIVE_PORTAL_CHECK)
        intent.putExtra(WifiManager.EXTRA_NETWORK_INFO, networkInfo)

        // Act
        connectivityChecker.onNetworkStateChangeReceive(intent)

        // Assert
        val expectedWifiStatus = createWifiStatusMessage(Status.CONNECTING, Signal.GOOD, false)
        verify(wifidServer).sendToAll(expectedWifiStatus)
    }

    @Test
    fun when_ConnectivityActionIntentReceived_then_properWifiStatusIsSent() {
        // Arrange
        connectivityChecker.setState(false,
                DetailedState.CONNECTED,
                Status.CONNECTED,
                Signal.GOOD)

        val intent = Intent(ConnectivityManager.CONNECTIVITY_ACTION)
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        shadowOf(connectivityManager).setActiveNetworkInfo(null)

        // Act
        connectivityChecker.onNetworkStateChangeReceive(intent)

        // Assert
        val expectedWifiStatus = createWifiStatusMessage(Status.NOT_CONNECTED, Signal.GOOD, false)
        verify(wifidServer).sendToAll(expectedWifiStatus)
    }

    @Test
    fun when_ConnectivityActionIntentReceived_then_properWifiStatusIsSent_2() {
        // Arrange
        connectivityChecker.setState(false,
                DetailedState.CONNECTED,
                Status.CONNECTED,
                Signal.GOOD)

        val intent = Intent(ConnectivityManager.CONNECTIVITY_ACTION)
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        shadowOf(connectivityManager.activeNetworkInfo).setDetailedState(DetailedState.AUTHENTICATING)

        // Act
        connectivityChecker.onNetworkStateChangeReceive(intent)

        // Assert
        val expectedWifiStatus = createWifiStatusMessage(Status.CONNECTING, Signal.GOOD, false)
        verify(wifidServer).sendToAll(expectedWifiStatus)
    }
}
