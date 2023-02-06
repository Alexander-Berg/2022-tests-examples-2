package com.yandex.launcher.updaterapp.core

import com.yandex.launcher.updaterapp.contract.models.Downloadable
import com.yandex.tv.services.platform.packages.PackagesServiceSdk2
import org.hamcrest.Matchers.not
import org.hamcrest.Matchers.nullValue
import org.hamcrest.MatcherAssert.assertThat
import org.junit.Test

class OperationContextRegistryTest {

    @Test
    fun `registry successfully created without crash`() {
        OperationContextRegistry(arrayOf(OperationContext1(), OperationContext2(), OperationContext3()))
    }

    @Test
    fun `registry contains all the registered elements`() {
        val registry = OperationContextRegistry(arrayOf(OperationContext1(), OperationContext2(), OperationContext3()))

        assertThat(registry.tryToObtainOperationContext(OperationContext1::class.java), not(nullValue()))
        assertThat(registry.tryToObtainOperationContext(OperationContext2::class.java), not(nullValue()))
        assertThat(registry.tryToObtainOperationContext(OperationContext3::class.java), not(nullValue()))
    }

    @Test(expected = IllegalArgumentException::class)
    fun `registry throws an exception when trying to obtain not registered item`() {
        val registry = OperationContextRegistry(arrayOf(OperationContext1(), OperationContext2(), OperationContext3()))

        registry.tryToObtainOperationContext(OperationContext4::class.java)
    }

    private class OperationContext1 : EmptyOperationContext()

    private class OperationContext2 : EmptyOperationContext()

    private class OperationContext3 : EmptyOperationContext()

    private class OperationContext4 : EmptyOperationContext()

    private abstract class EmptyOperationContext : OperationContext {

        override fun onDownloadFailed(item: Downloadable, error: DownloadError) = throw UnsupportedOperationException()

        override fun getItemsStorage() = throw UnsupportedOperationException()

        override fun getMetrica() = throw UnsupportedOperationException()

        override fun getSettings() = throw UnsupportedOperationException()

        override fun getErrorHandler() = throw UnsupportedOperationException()

        override fun getContext() = throw UnsupportedOperationException()

        override fun getSystemInfoProvider() = throw UnsupportedOperationException()

        override fun getDownloadDirectory() = throw UnsupportedOperationException()

        override fun getNotifier() = throw UnsupportedOperationException()

        override fun getBlockList() = throw UnsupportedOperationException()

        override fun onDownloaded(item: Downloadable, localPath: String) = throw UnsupportedOperationException()

        override fun onDownloadCancelled(downloadable: Downloadable) = throw UnsupportedOperationException()

        override fun getInstallLifecycleHandler() = throw UnsupportedOperationException()

        override fun getTimeUtils() = throw UnsupportedOperationException()

        override fun getScheduler() = throw UnsupportedOperationException()

        override fun getInstallerConfig() = throw UnsupportedOperationException()

        override fun contextTypeForMetrica() = "empty"

        override fun getPackagesSdk() = throw UnsupportedOperationException()
    }
}
