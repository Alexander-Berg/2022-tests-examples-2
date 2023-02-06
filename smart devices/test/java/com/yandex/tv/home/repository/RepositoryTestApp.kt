package com.yandex.tv.home.repository

import android.app.Application
import com.yandex.launcher.logger.Logger
import com.yandex.tv.common.connectivity.ConnectivityReceiver
import com.yandex.tv.common.network.MetricaLoggingInterceptor
import com.yandex.tv.common.network.NetworkConfigHolder
import com.yandex.tv.common.statistics.ResponseHeadersTracker
import com.yandex.tv.home.di.AuthHeaderHolder
import com.yandex.tv.home.policy.PolicyManager
import com.yandex.tv.home.pulse.PulseDelegate
import com.yandex.tv.home.pulse.PulseDelegateNoop
import com.yandex.tv.home.utils.ConsoleLogProcessor
import com.yandex.tv.home.utils.HttpRequestManager
import com.yandex.tv.home.utils.ThreadPolicy
import com.yandex.tv.services.metrica.MetricaServiceSdk2
import org.koin.dsl.module
import org.koin.dsl.onClose
import org.mockito.Mockito
import org.mockito.kotlin.spy

class RepositoryTestApp : Application() {

    override fun onCreate() {
        super.onCreate()
        Logger.setProcessor(ConsoleLogProcessor())
    }
}

val repositoryTestModule = module {
    single { spy(PolicyManager(get(), get(), get())).also { it.init() } } onClose { it?.destroy() }

    single {
        spy(
            HttpRequestManager(
                get<ThreadPolicy>().baseIOExecutor,
                ConnectivityReceiver(get(), get())
            )
        ).also { it.init() }
    }

    single { ResponseHeadersTracker(Mockito.mock(MetricaServiceSdk2::class.java)) }

    single<PulseDelegate> { PulseDelegateNoop() }

    single { NetworkConfigHolder(get()) }

    factory { AuthHeaderHolder(null) }

    single {
        MetricaLoggingInterceptor().also {
            it.level = MetricaLoggingInterceptor.Level.NONE
        }
    }
}
