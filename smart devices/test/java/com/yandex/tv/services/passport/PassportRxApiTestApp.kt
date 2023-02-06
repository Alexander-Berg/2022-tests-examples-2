// Copyright 2021 Yandex LLC. All rights reserved.

package com.yandex.tv.services.passport

import android.app.Application
import android.content.res.Resources
import org.mockito.kotlin.anyOrNull
import org.mockito.kotlin.doReturn
import org.mockito.kotlin.mock
import com.yandex.tv.common.AppInfoProvider
import com.yandex.tv.common.config.di.DeviceComponent
import com.yandex.tv.common.di.NetworkComponent
import com.yandex.tv.common.metrica.MetricaIdentifiersProvider
import com.yandex.tv.services.metrica.MetricaServiceSdk2
import com.yandex.tv.services.passport.gift.GiftComponent
import org.mockito.Mockito.spy

class PassportRxApiTestApp : Application() {

    override fun onCreate() {
        super.onCreate()
        val metricaSdk = spy(MetricaServiceSdk2::class.java)
        DeviceComponent.instance = spy(DeviceComponent::class.java)
        NetworkComponent.instance = spy(
            NetworkComponent(
                this,
                DeviceComponent.instance,
                metricaSdk,
                AppInfoProvider("package.test", "class.test", 123),
                TestMetricaIdentifiersProvider(),
                PassportTokenProvider(),
                null
            )
        )
        GiftComponent.instance = spy(
            GiftComponent(
                NetworkComponent.instance,
                mock()
            )
        )
        PassportComponent.instance = spy(
            PassportComponent(
                NetworkComponent.instance,
                GiftComponent.instance,
                mock()
            )
        )
    }

    override fun getResources(): Resources {
        val resSpy = spy(super.getResources())
        doReturn("test string").`when`(resSpy).getString(anyOrNull())
        return resSpy
    }
}

class TestMetricaIdentifiersProvider : MetricaIdentifiersProvider {
    override fun getUuid(): String? {
        return "test_uuid"
    }

    override fun getDeviceId(): String? {
        return "test_deviceid"
    }
}
