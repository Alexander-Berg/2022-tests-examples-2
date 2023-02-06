package ru.yandex.quasar.glagol.impl

import android.net.nsd.NsdManager
import android.net.nsd.NsdServiceInfo
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.`is`
import org.hamcrest.Matchers.equalTo
import org.junit.Test
import org.mockito.Mockito
import ru.yandex.quasar.glagol.Config

class NsdServiceResolverTest {

    @Test
    fun testRetries() {
        val config = Config.Builder().discoveryMdnsResolveRetries(5).build()
        val listener = DummyListener()
        val resolveProcessor = FailedResolveProcessor()
        val resolver = NsdServiceResolver(resolveProcessor, config, listener)
        resolver.resolve(generateServiceInfo())

        assertThat(listener.failCalled, `is`(true))
        assertThat(resolveProcessor.callCounter, `is`(equalTo(5)))

    }

    private fun generateServiceInfo() : NsdServiceInfo {
        val service: NsdServiceInfo = Mockito.mock(NsdServiceInfo::class.java)
        val serviceName = "Ololo-${Math.random()}"
        Mockito.`when`(service.serviceName).thenReturn(serviceName)
        return service
    }

    class FailedResolveProcessor: NsdServiceResolver.ResolveProcessor {
        var callCounter = 0

        override fun resolve(serviceInfo: NsdServiceInfo, listener: NsdManager.ResolveListener) {
            callCounter++
            listener.onResolveFailed(serviceInfo, NsdManager.FAILURE_ALREADY_ACTIVE)
        }
    }

    class DummyListener : NsdServiceResolver.Listener {
        var failCalled = false
        var successCalled = false

        override fun onResolveSuccess(serviceInfo: NsdServiceInfo) {
            successCalled = true
        }

        override fun onResolveFail(serviceInfo: NsdServiceInfo, errCode: Int) {
            failCalled = true
        }
    }

}
