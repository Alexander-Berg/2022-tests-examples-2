package com.yandex.tv.services.passport

import com.yandex.io.sdk.registration.RegistrationResult
import com.yandex.io.sdk.registration.YandexIoRegistrationServiceSdk2
import com.yandex.tv.services.common.ServiceFuture
import java.util.concurrent.TimeUnit

class RegistrationServiceSdk2Test: YandexIoRegistrationServiceSdk2 {
    override fun isShutdown(): Boolean {
        return false
    }

    override fun shutdown() {
    }

    override fun shutdownNow() {
    }

    override fun registerDeviceInBackend(
        oauthToken: String?,
        uid: String?
    ): ServiceFuture<RegistrationResult> {
        return FakeServiceFuture(RegistrationResult(true, 200, null))
    }

    private inner class FakeServiceFuture<T>(private val result: T): ServiceFuture<T> {
        override fun cancel(mayInterruptIfRunning: Boolean): Boolean {
            return false
        }

        override fun isCancelled(): Boolean {
            return false
        }

        override fun isDone(): Boolean {
            return true
        }

        override fun get(): T {
            return result
        }

        override fun get(timeout: Long, unit: TimeUnit?): T {
            return result
        }

        override fun getSafely(): T? {
            return result
        }

        override fun getSafely(timeout: Long, unit: TimeUnit): T? {
            return result
        }

        override fun getSafely(defaultValue: T?): T? {
            return result
        }

        override fun getSafely(timeout: Long, unit: TimeUnit, defaultValue: T?): T? {
            return result
        }

        override fun setCallbacks(
            onSuccess: ServiceFuture.Consumer<T>,
            onError: ServiceFuture.Consumer<Throwable>
        ): Boolean {
            return true
        }
    }
}
