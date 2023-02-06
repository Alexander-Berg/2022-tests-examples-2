package com.yandex.tv.videoplayer.contract

import android.app.Application
import com.google.android.exoplayer2.Player
import org.mockito.kotlin.any
import org.mockito.kotlin.anyOrNull
import org.mockito.kotlin.doReturn
import org.mockito.kotlin.mock
import org.mockito.kotlin.spy
import com.yandex.tv.common.AppInfoProvider
import com.yandex.tv.common.DeviceInfoProvider
import com.yandex.tv.common.QuasarDevice
import com.yandex.tv.common.config.di.DeviceComponent
import com.yandex.tv.common.di.NetworkComponent
import com.yandex.tv.common.metrica.MetricaIdentifiersProvider
import com.yandex.tv.common.network.MetricaLoggingInterceptor
import com.yandex.tv.common.ott.OttConfig
import com.yandex.tv.services.experiments.ExperimentsHelper
import com.yandex.tv.services.policymanagerservice.Policy
import com.yandex.tv.videoplayer.BuildConfig
import com.yandex.tv.videoplayer.IPlayerModelFactory
import com.yandex.tv.videoplayer.PlayerContract
import com.yandex.tv.videoplayer.common.di.PlayerAppComponent
import ru.yandex.video.config.AccountProvider
import ru.yandex.video.data.dto.VideoData
import ru.yandex.video.ott.data.repository.ManifestRepository
import ru.yandex.video.player.YandexPlayer

class VideoPlayerContractTestApp : Application(), IPlayerModelFactory {

    override fun onCreate() {
        super.onCreate()
        setupDeviceComponent()
        setupAppComponent(DeviceComponent.instance)
    }

    private fun setupAppComponent(deviceComponent: DeviceComponent) {
        val appInfoProvider = AppInfoProvider(BuildConfig.APPLICATION_ID, BuildConfig.VERSION_NAME, BuildConfig.VERSION_CODE)
        val appComponent = spy(PlayerAppComponent(this, deviceComponent, appInfoProvider, mock(), mock()))
        val playerFactories = spy(appComponent.playerFactories)
        val player = mock<YandexPlayer<Player>>()
        doReturn(player).`when`(playerFactories).createPlayer(any(), any(), anyOrNull())
        doReturn(playerFactories).`when`(appComponent).playerFactories
        PlayerAppComponent.instance = appComponent
    }

    private fun setupDeviceComponent() {
        DeviceComponent.instance = mock()
        val quasarDevice = mock<QuasarDevice>()
        doReturn("deviceId").`when`(quasarDevice).deviceId
        doReturn(quasarDevice).`when`(DeviceComponent.instance).quasarDevice
        doReturn(mock<DeviceInfoProvider>()).`when`(DeviceComponent.instance).deviceInfoProvider
    }

    override fun createModel(
        accountProvider: AccountProvider,
        policy: Policy,
        experimentsHelper: ExperimentsHelper,
        metricaIdentifiersProvider: MetricaIdentifiersProvider,
        manifest: ManifestRepository<out VideoData>,
        metricaLoggingInterceptor: MetricaLoggingInterceptor,
        networkComponent: NetworkComponent,
        ottConfig: OttConfig
    ): PlayerContract.Model {
        return EmptyPlayerModel()
    }
}
