package com.yandex.tv.common.utility.test

import android.os.Bundle
import com.yandex.tv.services.common.ServiceFuture
import com.yandex.tv.services.common.internal.CompletableServiceFuture
import com.yandex.tv.services.metrica.MetricaServiceSdk2
import com.yandex.tv.services.policymanagerservice.Policy
import com.yandex.tv.services.policymanagerservice.PolicyManagerServiceSdk2
import com.yandex.tv.services.quasar.QuasarServiceSdk2

class EmptyPolicyManagerServiceSdk2 : PolicyManagerServiceSdk2 {
    override fun getPolicy(): ServiceFuture<Policy> {
        return CompletableServiceFuture<Policy>().also { it.complete(Policy()) }
    }

    override fun isSiteAvailable(hostName: String?): ServiceFuture<Boolean> {
        return CompletableServiceFuture<Boolean>().also { it.complete(true) }
    }

    override fun isAppAvailable(packageName: String?): ServiceFuture<Boolean> {
        return CompletableServiceFuture<Boolean>().also { it.complete(true) }
    }

    override fun isTvProgramAvailable(restrictionAge: Int): ServiceFuture<Boolean> {
        return CompletableServiceFuture<Boolean>().also { it.complete(true) }
    }

    override fun shutdown() {
        //noop
    }

    override fun isShutdown(): Boolean {
        return false
    }

    override fun shutdownNow() {
        //noop
    }
}

class EmptyMetricaServiceSdk2 : MetricaServiceSdk2 {

    override fun sendJsonBatch(eventArray: String?): ServiceFuture<Void> {
        return CompletableServiceFuture<Void>().also { it.complete(null) }
    }

    override fun getUuid(): ServiceFuture<String> {
        return CompletableServiceFuture<String>().also { it.complete("") }
    }

    override fun shutdown() {
        //noop
    }

    override fun getDeviceId(): ServiceFuture<String> {
        return CompletableServiceFuture<String>().also { it.complete("") }
    }

    override fun isShutdown(): Boolean {
        return false
    }

    override fun shutdownNow() {
        //noop
    }

    override fun processEvent(type: Int, param: Bundle?): ServiceFuture<Void> {
        return CompletableServiceFuture<Void>().also { it.complete(null) }
    }
}

class EmptyQuasarServiceSdk2 : QuasarServiceSdk2 {
    override fun shutdown() {
        //noop
    }

    override fun isShutdown(): Boolean {
        return false
    }

    override fun shutdownNow() {
        //noop
    }

    override fun getQuasarDeviceId(): ServiceFuture<String> {
        return CompletableServiceFuture<String>().also { it.complete("") }
    }

    override fun makeTandem(speakerDeviceId: String, speakerPlatform: String): ServiceFuture<Void> {
        return CompletableServiceFuture<Void>().also { it.complete(null) }
    }

    override fun removeTandem(groupId: Int): ServiceFuture<Void> {
        return CompletableServiceFuture<Void>().also { it.complete(null) }
    }

    override fun getQuasarPlatform(): ServiceFuture<String> {
        return CompletableServiceFuture<String>().also { it.complete("") }
    }
}
