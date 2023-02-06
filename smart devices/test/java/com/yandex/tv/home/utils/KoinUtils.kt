package com.yandex.tv.home.utils

import android.os.HandlerThread
import com.yandex.io.sdk.alice.YandexIoAliceSdk
import com.yandex.tv.common.utility.test.EmptyMetricaServiceSdk2
import com.yandex.tv.common.utility.test.EmptyPolicyManagerServiceSdk2
import com.yandex.tv.common.utility.test.EmptyQuasarServiceSdk2
import com.yandex.tv.home.di.DEPENDENCY_MAIN_LOOPER
import com.yandex.tv.home.di.injectMainLooper
import com.yandex.tv.services.metrica.MetricaServiceSdk2
import com.yandex.tv.services.policymanagerservice.PolicyManagerServiceSdk2
import com.yandex.tv.services.quasar.QuasarServiceSdk2
import org.koin.core.context.GlobalContext
import org.koin.core.qualifier.named
import org.koin.dsl.module
import org.koin.dsl.onClose
import org.mockito.kotlin.mock
import org.robolectric.Shadows
import java.util.concurrent.Executors
import java.util.concurrent.ScheduledExecutorService
import java.util.concurrent.TimeUnit

val commonTestModule = module {

    single<MetricaServiceSdk2>(createdAtStart = true) { EmptyMetricaServiceSdk2() } onClose { it?.shutdownNow() }
    single<PolicyManagerServiceSdk2>(createdAtStart = true) { EmptyPolicyManagerServiceSdk2() } onClose { it?.shutdownNow() }
    single<QuasarServiceSdk2>(createdAtStart = true) { EmptyQuasarServiceSdk2() } onClose { it?.shutdownNow() }
    single<YandexIoAliceSdk>(createdAtStart = true) { mock() }

    single(createdAtStart = true) { ThreadPolicy(false) } onClose { it?.destroy() }

    single(qualifier = named(DEPENDENCY_MAIN_LOOPER)) { HandlerThread("MockMainThread").apply { start() }.looper } onClose { it?.quit() }

    //dirty hack to advance "main looper" clock to make postDelayed work
    //koin module scoped because "main looper" is recreated for each test
    single<Runnable>(qualifier = named("clockAdvanceRunnable")) {
        object : Runnable {
            override fun run() {
                Shadows.shadowOf(injectMainLooper()).scheduler.advanceBy(1, TimeUnit.SECONDS)
                getClockAdvancer().schedule(this , 1, TimeUnit.SECONDS)
            }
        }
    }
    single<ScheduledExecutorService>(createdAtStart = true, qualifier = named("clockAdvancer")) {
        Executors.newSingleThreadScheduledExecutor().also {
            it.schedule(getClockAdvanceRunnable(), 1, TimeUnit.SECONDS)
        }
    } onClose {
        it?.shutdownNow()
    }
}

private fun getClockAdvancer(): ScheduledExecutorService {
    return GlobalContext.get().get(qualifier = named("clockAdvancer"))
}

private fun getClockAdvanceRunnable(): Runnable {
    return GlobalContext.get().get(qualifier = named("clockAdvanceRunnable"))
}
