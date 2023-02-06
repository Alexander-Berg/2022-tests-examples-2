package com.yandex.tv.home.informer

import android.content.ContentResolver
import android.content.Context
import android.database.ContentObserver
import android.net.wifi.WifiConfiguration
import android.net.wifi.WifiManager
import android.os.Build
import android.provider.Settings
import androidx.test.core.app.ApplicationProvider
import com.yandex.tv.common.connectivity.ConnectivityReceiver
import com.yandex.tv.home.contract.HomeAppContractTestApp
import com.yandex.tv.home.contract.deeplinkTestModule
import com.yandex.tv.home.di.homeAppModule
import com.yandex.tv.home.utils.commonTestModule
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers
import org.junit.*
import org.junit.runner.RunWith
import org.koin.android.ext.koin.androidContext
import org.koin.core.context.startKoin
import org.koin.core.context.stopKoin
import org.koin.test.KoinTest
import org.mockito.Mockito.*
import org.mockito.kotlin.doReturn
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.shadows.ShadowLooper.runUiThreadTasksIncludingDelayedTasks


@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.P], application = HomeAppContractTestApp::class)
class InformersDataProviderTest : KoinTest {

    private val connectivityReceiver = mock(ConnectivityReceiver::class.java)
    private val context: Context = mock(Context::class.java)
    private val applicationContext = mock(Context::class.java)
    private val wifiManager = mock(WifiManager::class.java)
    private val formatChangeObserver = mock(ContentObserver::class.java)
    private val contentResolver = mock(ContentResolver::class.java)
    private val wifiConfiguration = mock(WifiConfiguration::class.java)

    @Before
    fun setUp() {
        startKoin {
            androidContext(ApplicationProvider.getApplicationContext())
            modules(listOf(homeAppModule, commonTestModule, deeplinkTestModule))
        }
        whenever(context.applicationContext).doReturn(applicationContext)
        whenever(applicationContext.getSystemService(WifiManager::class.java)).doReturn(wifiManager)
        val uri = Settings.System.getUriFor(Settings.System.TIME_12_24)
        whenever(context.contentResolver).doReturn(contentResolver)
        whenever(context.contentResolver.registerContentObserver(uri, true, formatChangeObserver)).then {}
    }

    @After
    fun clear() {
        stopKoin()
    }

    @Test
    fun `cold start for networks`() {
        val informersDataProvider = InformersDataProvider(connectivityReceiver, null)
        whenever(wifiManager.isWifiEnabled).doReturn(true)
        whenever(wifiManager!!.configuredNetworks).doReturn(mutableListOf(wifiConfiguration))
        informersDataProvider.init(context)
        assertThat(
            informersDataProvider.connectionErrorData,
            Matchers.equalTo(ConnectionErrorData.WAITING_FOR_CONNECTION)
        )
        runUiThreadTasksIncludingDelayedTasks()
        assertThat(informersDataProvider.connectionErrorData, Matchers.equalTo(ConnectionErrorData.DISCONNECTED))
    }

    @Test
    fun `hot start for networks`() {
        val informersDataProvider = InformersDataProvider(connectivityReceiver, null)
        informersDataProvider.init(context)
        informersDataProvider.onScreenStateChanged(false, true)
        informersDataProvider.onScreenStateChanged(true, false)
        assertThat(
            informersDataProvider.connectionErrorData,
            Matchers.equalTo(ConnectionErrorData.WAITING_FOR_CONNECTION)
        )

        informersDataProvider.onScreenStateChanged(false, true)
        informersDataProvider.onScreenStateChanged(true, false)
        assertThat(
            informersDataProvider.connectionErrorData,
            Matchers.equalTo(ConnectionErrorData.WAITING_FOR_CONNECTION)
        )

        informersDataProvider.onConnectivityChanged(true, 0, "")
        assertThat(informersDataProvider.connectionErrorData, Matchers.equalTo(ConnectionErrorData.CONNECTED))
    }

    @Test
    fun `base changes in connectionErrorData`() {
        val informersDataProvider = InformersDataProvider(connectivityReceiver, null)
        informersDataProvider.init(ApplicationProvider.getApplicationContext())

        informersDataProvider.onConnectivityChanged(true, 0, "")
        assertThat(informersDataProvider.connectionErrorData, Matchers.equalTo(ConnectionErrorData.CONNECTED))

        whenever(connectivityReceiver.isConnecting).doReturn(true)
        informersDataProvider.onConnectivityChanged(false, 0, "")
        assertThat(informersDataProvider.connectionErrorData, Matchers.equalTo(ConnectionErrorData.CONNECTING))

        whenever(connectivityReceiver.isConnecting).doReturn(false)
        informersDataProvider.onConnectivityChanged(false, 0, "")
        runUiThreadTasksIncludingDelayedTasks()
        assertThat(informersDataProvider.connectionErrorData, Matchers.equalTo(ConnectionErrorData.DISCONNECTED))
    }
}

