package ru.yandex.quasar.app.screensaver.screenSaverConfigurators

import android.content.Context
import android.content.SharedPreferences
import android.os.Handler
import android.os.HandlerThread
import okhttp3.Request
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito
import org.mockito.kotlin.any
import org.mockito.kotlin.argumentCaptor
import org.mockito.kotlin.eq
import org.mockito.kotlin.inOrder
import org.mockito.kotlin.mock
import org.mockito.kotlin.never
import org.mockito.kotlin.timeout
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.powermock.api.mockito.PowerMockito
import org.powermock.core.classloader.annotations.PrepareForTest
import org.powermock.modules.junit4.PowerMockRunner
import ru.yandex.quasar.app.configs.*
import ru.yandex.quasar.app.screensaver.screenSaverHelpers.ScreenSaverImageLoader
import ru.yandex.quasar.app.screensaver.screenSaverHelpers.ScreenSaverMediaLoader
import ru.yandex.quasar.app.utils.HttpClient
import ru.yandex.quasar.app.video.hdmi.HdmiObservable
import ru.yandex.quasar.fakes.FakeExecutorService
import ru.yandex.quasar.core.utils.Observable
import java.util.concurrent.ScheduledFuture

@RunWith(PowerMockRunner::class)
@PrepareForTest(ScreenSaverConfiguratorService::class)
class ScreenSaverConfiguratorServiceTest {
    private val context: Context = mock()
    private val preferences: SharedPreferences = mock()
    private val externalConfigObservable: ExternalConfigObservable = mock()
    private val hdmiObservable: HdmiObservable = mock()
    private val mediaLoader: ScreenSaverMediaLoader = mock()
    private val httpClient: HttpClient = mock()
    private val imageLoader: ScreenSaverImageLoader = mock()
    private val handlerThread: HandlerThread = mock()

    private val fakeExecutorService = FakeExecutorService()
    private val future: ScheduledFuture<Any> = mock()

    private val requestBuilder: Request.Builder = mock()

    private val stationConfig: StationConfig = mock()
    private val deviceConfig: DeviceConfig = mock()
    private val screenSaverConfig: ScreenSaverSystemConfig = mock()

    private lateinit var configuratorService: ScreenSaverConfiguratorService

    @Before
    fun setUp() {
        PowerMockito.whenNew(HandlerThread::class.java).withAnyArguments().thenReturn(handlerThread)

        whenever(context.getSharedPreferences(any(), any())).thenReturn(preferences)
        whenever(httpClient.newRequest()).thenReturn(requestBuilder)
        whenever(requestBuilder.url(Mockito.anyString())).thenReturn(requestBuilder)
        whenever(preferences.edit()).thenReturn(mock())

        val systemConfig: SystemConfig = mock()
        whenever(stationConfig.systemConfig).thenReturn(systemConfig)
        whenever(stationConfig.deviceConfig).thenReturn(deviceConfig)
        whenever(systemConfig.screenSaverConfig).thenReturn(screenSaverConfig)

        whenever(future.isDone).thenReturn(true)
        whenever(future.cancel(any())).thenReturn(true)
    }

    private fun initService() {
        configuratorService =
            ScreenSaverConfiguratorService(
                externalConfigObservable,
                hdmiObservable,
                imageLoader,
                mediaLoader,
                mock(),
                context,
                httpClient,
                fakeExecutorService,
                mock(),
                mock()
            )
        fakeExecutorService.runAllJobs()
    }

    private fun <T : Any?> Observable.Observer<T>.updateConfigAndRun(config: T) {
        this.update(config)
        fakeExecutorService.runAllJobs()
    }

    @Test
    fun given_noPreferences_when_initService_then_noLoadingStarted() {
        // create configurator service
        initService()

        // httpClient.execute hasn't to be called
        verify(httpClient, never()).execute(any(), any())
    }

    @Test
    fun given_preferences_when_initService_then_startLoading() {
        // init preferences
        whenever(preferences.getString(any(), eq(null))).thenReturn("testConfigUrl")

        // create configurator service
        initService()

        // httpClient.execute has to be called
        verify(httpClient, timeout(1000)).execute(any(), any())
    }

    @Test
    fun given_configuratorService_when_systemConfigChanged_then_loadingHasRestarted() {
        // init config for update and create configurator service
        whenever(screenSaverConfig.defaultType).thenReturn(ScreenSaverType.IMAGE)
        whenever(screenSaverConfig.getContentUrl(any(), any())).thenReturn("testConfigUrl")
        initService()

        // capture observer and update config
        lateinit var stationConfigObserver: Observable.Observer<StationConfig>
        argumentCaptor<Observable.Observer<StationConfig>> {
            verify(externalConfigObservable).addObserver(capture())
            stationConfigObserver = firstValue
        }
        stationConfigObserver.updateConfigAndRun(stationConfig)

        // all data has to be cleared and new loading has to be started
        verify(mediaLoader).clearQueue()
        verify(httpClient).execute(any(), any())
    }

    @Test
    fun given_configurationService_when_systemConfigChangedTwiceWithTheSameUrl_then_loadingHasNotRestarted() {
        // init config for update and create configurator service
        whenever(screenSaverConfig.defaultType).thenReturn(ScreenSaverType.IMAGE)
        whenever(screenSaverConfig.getContentUrl(any(), any())).thenReturn("testConfigUrl")
        initService()

        // capture observer
        lateinit var stationConfigObserver: Observable.Observer<StationConfig>
        argumentCaptor<Observable.Observer<StationConfig>> {
            verify(externalConfigObservable).addObserver(capture())
            stationConfigObserver = firstValue
        }

        inOrder(mediaLoader, httpClient) {
            // update config
            stationConfigObserver.updateConfigAndRun(stationConfig)

            // new loading has started
            verify(mediaLoader).clearQueue()
            verify(httpClient).execute(any(), any())

            // update to the same config
            stationConfigObserver.updateConfigAndRun(stationConfig)

            // new loading hasn't started
            verify(mediaLoader, never()).clearQueue()
            verify(httpClient, never()).execute(any(), any())
        }
    }

    @Test
    fun given_configurationService_when_systemConfigChangedTwice_then_loadingHasRestarted() {
        // init config for update and create configurator service
        whenever(screenSaverConfig.defaultType).thenReturn(ScreenSaverType.IMAGE)
        whenever(screenSaverConfig.getContentUrl(any(), any())).thenReturn("testConfigUrl")
        initService()

        // capture observer
        lateinit var stationConfigObserver: Observable.Observer<StationConfig>
        argumentCaptor<Observable.Observer<StationConfig>> {
            verify(externalConfigObservable).addObserver(capture())
            stationConfigObserver = firstValue
        }

        inOrder(mediaLoader, httpClient) {
            // update config
            stationConfigObserver.updateConfigAndRun(stationConfig)

            // new loading has started
            verify(mediaLoader).clearQueue()
            verify(httpClient).execute(any(), any())

            // update to config with different url
            whenever(screenSaverConfig.getContentUrl(any(), any())).thenReturn("testConfigUrl2")
            stationConfigObserver.updateConfigAndRun(stationConfig)

            // new loading has been started
            verify(mediaLoader).clearQueue()
            verify(httpClient).execute(any(), any())
        }
    }

    @Test
    fun given_configurationService_when_deviceConfigChanged_then_loadingHasRestarted() {
        // init system configs and create backend configurator
        whenever(screenSaverConfig.defaultType).thenReturn(ScreenSaverType.IMAGE)
        whenever(
            screenSaverConfig.getContentUrl(
                eq(ScreenSaverType.IMAGE),
                any()
            )
        ).thenReturn("systemConfigUrl")
        initService()

        // capture observer
        lateinit var stationConfigObserver: Observable.Observer<StationConfig>
        argumentCaptor<Observable.Observer<StationConfig>> {
            verify(externalConfigObservable).addObserver(capture())
            stationConfigObserver = firstValue
            stationConfigObserver.updateConfigAndRun(stationConfig)
        }

        // init device config
        val userConfig: ScreenSaverDeviceConfig = mock()
        whenever(deviceConfig.screenSaverConfig).thenReturn(userConfig)
        whenever(userConfig.type).thenReturn(ScreenSaverType.VIDEO)
        whenever(
            screenSaverConfig.getContentUrl(
                eq(ScreenSaverType.VIDEO),
                any()
            )
        ).thenReturn("userConfigUrl")

        inOrder(mediaLoader, httpClient) {
            // first loading has been started
            verify(mediaLoader).clearQueue()
            verify(httpClient).execute(any(), any())

            // update device config
            stationConfigObserver.updateConfigAndRun(stationConfig)

            // new loading has been started
            verify(mediaLoader).clearQueue()
            verify(httpClient).execute(any(), any())
        }
    }

    @Test
    fun given_configurationService_when_deviceConfigChangedTwice_then_loadingHasRestarted() {
        // init device config for update and create configurator service
        val userConfig: ScreenSaverDeviceConfig = mock()
        whenever(deviceConfig.screenSaverConfig).thenReturn(userConfig)
        whenever(userConfig.type).thenReturn(ScreenSaverType.IMAGE)
        whenever(screenSaverConfig.getContentUrl(any(), any())).thenReturn("userConfigUrl")
        initService()

        // capture observer
        lateinit var stationConfigObserver: Observable.Observer<StationConfig>
        argumentCaptor<Observable.Observer<StationConfig>> {
            verify(externalConfigObservable).addObserver(capture())
            stationConfigObserver = firstValue
        }

        inOrder(mediaLoader, httpClient) {
            // update device config
            stationConfigObserver.updateConfigAndRun(stationConfig)

            // new loading has started
            verify(mediaLoader).clearQueue()
            verify(httpClient).execute(any(), any())

            // update device to config with different url
            whenever(screenSaverConfig.getContentUrl(any(), any())).thenReturn("userConfigUrl2")
            stationConfigObserver.updateConfigAndRun(stationConfig)

            // new loading has been started
            verify(mediaLoader).clearQueue()
            verify(httpClient).execute(any(), any())
        }
    }

    @Test
    @PrepareForTest(ScreenSaverConfiguratorService::class)
    fun given_hdmiTurnedOff_when_postDelayed_then_delayCalled() {
        // mock handler creation to verify postDelayed and create configurator service
        val handler: Handler = mock()
        val backendConfigurator: ScreenSaverBackendConfigurator = mock()
        PowerMockito.whenNew(Handler::class.java).withAnyArguments().thenReturn(handler)
        PowerMockito.whenNew(ScreenSaverBackendConfigurator::class.java).withAnyArguments()
            .thenReturn(backendConfigurator)
        initService()

        // call immediate update
        configuratorService.delayUpdate(0)

        // verify handler cleared and call postDelay
        inOrder(handler) {
            verify(handler).removeCallbacksAndMessages(eq(null))
            verify(handler).postDelayed(any(), eq(0))
        }
        // capture delayed task and call it
        argumentCaptor<Runnable> {
            verify(handler).postDelayed(capture(), eq(0))
            val delayedTask = firstValue
            delayedTask.run()
        }

        // postDelay has been called and new item not loaded
        verify(handler).postDelayed(any(), eq(10_000))
        verify(backendConfigurator, never()).next
    }


    @Test
    @PrepareForTest(ScreenSaverConfiguratorService::class)
    fun given_hdmiTurnedOn_when_postDelayed_then_nextItemIsLoaded() {
        // mock handler creation to verify postDelayed and create configurator service
        val handler: Handler = mock()
        val backendConfigurator: ScreenSaverBackendConfigurator = mock()
        PowerMockito.whenNew(Handler::class.java).withAnyArguments().thenReturn(handler)
        PowerMockito.whenNew(ScreenSaverBackendConfigurator::class.java).withAnyArguments()
            .thenReturn(backendConfigurator)
        initService()

        // capture hdmiObsever and send hdmiConnected to true
        lateinit var hdmiObserver: Observable.Observer<Boolean>
        argumentCaptor<Observable.Observer<Boolean>> {
            verify(hdmiObservable).addObserver(capture())
            hdmiObserver = firstValue
        }
        hdmiObserver.updateConfigAndRun(true)

        // call immediate update
        configuratorService.delayUpdate(0)

        // verify handler cleared and call postDelay
        inOrder(handler) {
            verify(handler).removeCallbacksAndMessages(eq(null))
            verify(handler).postDelayed(any(), eq(0))
        }
        // capture delayed task and call it
        argumentCaptor<Runnable> {
            verify(handler).postDelayed(capture(), eq(0))
            val delayedTask = firstValue
            delayedTask.run()
        }

        // backendConfigurator created and new item has been loaded
        verify(backendConfigurator).next
    }

    @Test
    @PrepareForTest(ScreenSaverConfiguratorService::class)
    fun given_configuratorService_when_destroy_then_allItemsAreDestroyed() {
        // mock handle creation and create configurator service
        val handler: Handler = mock()
        PowerMockito.whenNew(Handler::class.java).withAnyArguments().thenReturn(handler)
        initService()

        // destroy configurator service
        configuratorService.destroy()

        // verify all items has been destroyed
        verify(handler).removeCallbacksAndMessages(eq(null))
        verify(handlerThread).quit()
        verify(externalConfigObservable).removeObserver(any())
        verify(hdmiObservable).removeObserver(any())
        verify(mediaLoader).destroy()
        verify(imageLoader).destroy()
    }
}
