package com.yandex.io.shared.assets

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import com.yandex.io.shared.toFile
import org.junit.Assert
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import java.io.File

@RunWith(RobolectricTestRunner::class)
class IOSdkAssetsManagerTest {

    private val context = ApplicationProvider.getApplicationContext<Context>()
    private val assetsDir = "${context.filesDir}/iosdk/system".toFile()
    private val underTest = IOSdkAssetsManager(context, assetsDir, TEST_VERSION)

    @Test
    fun `unpack assets when not previously unpacked`() {
        underTest.unpackAssetsIfNeeded()

        Assert.assertTrue(underTest.quasarConfig.exists())
        Assert.assertTrue(underTest.caCertificates.exists())
    }

    @Test
    fun `unpack new version assets and remove previous ones`() {
        underTest.unpackAssetsIfNeeded()
        val newUnderTest = IOSdkAssetsManager(context, assetsDir, "2.0")

        newUnderTest.unpackAssetsIfNeeded()

        Assert.assertFalse(File(assetsDir, "1.0").exists())
        Assert.assertTrue(newUnderTest.quasarConfig.exists())
        Assert.assertTrue(newUnderTest.caCertificates.exists())
    }

    private companion object {
        private const val TEST_VERSION = "1.0"
    }
}
