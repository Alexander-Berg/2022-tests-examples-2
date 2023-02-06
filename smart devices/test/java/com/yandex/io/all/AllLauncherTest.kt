package com.yandex.io.all

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import com.yandex.io.AliceCapability
import com.yandex.io.Launcher
import com.yandex.io.shared.AndroidDeviceInfo
import com.yandex.io.shared.IOSdkDirs
import com.yandex.io.shared.IoSdkSettings
import com.yandex.io.shared.LibLoader
import com.yandex.io.shared.assets.IOSdkAssetsManager
import org.junit.Assert
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.argThat
import org.mockito.kotlin.inOrder
import org.mockito.kotlin.mock
import org.robolectric.RobolectricTestRunner
import org.robolectric.Shadows.shadowOf
import org.robolectric.annotation.Config
import org.robolectric.annotation.Implementation
import org.robolectric.annotation.Implements

@RunWith(RobolectricTestRunner::class)
@Config(shadows = [AllLauncherTest.ShadowLibLoader::class])
class AllLauncherTest {

    private val context = ApplicationProvider.getApplicationContext<Context>()

    init {
        // See https://github.com/robolectric/robolectric/issues/6271#issuecomment-983878322
        shadowOf(context.packageManager).getInternalMutablePackageInfo(context.packageName).versionName = "1"
    }

    private val dirs = IOSdkDirs(context)
    private val assetsManager = IOSdkAssetsManager(context, dirs.systemDir, "1.0")

    private val underTest = AllLauncher(object : AndroidDeviceInfo(context) {
        override val quasarPlatform: String = "test"
        override val quasarDeviceId: String = "test"
    }, IoSdkSettings.DEFAULT, dirs, assetsManager)

    private val launcher = mock<Launcher>()
    private val aliceCapability = mock<AliceCapability>()

    @Before
    fun setUp() {
        underTest.launcher = launcher
        underTest.aliceCapability = aliceCapability
    }

    @Test
    fun `launcher is initialized and started when launched`() {
        underTest.launch()

        Assert.assertEquals("quasar_daemons", ShadowLibLoader.loadedLib)
        Assert.assertTrue(assetsManager.quasarConfig.exists())
        inOrder(launcher) {
            verify(launcher).initialize(argThat { config ->
                config.hasDeviceId()
                        && config.paths.configPath == assetsManager.quasarConfig.path
                        && config.paths.workdirPath == dirs.workDir.path
                        && config.paths.getConfigPlaceholdersOrThrow("QUASAR") == assetsManager.quasarConfigDir.path
                        && config.paths.getConfigPlaceholdersOrThrow("FILES") == dirs.filesDir.path
                        && config.paths.getConfigPlaceholdersOrThrow("DATA") == dirs.dataDir.path
            })
            verify(launcher).start()
        }
    }

    @Implements(LibLoader::class)
    object ShadowLibLoader {

        var loadedLib: String? = null

        @Implementation
        @JvmStatic
        fun loadLibrary(libname: String) {
            loadedLib = libname
        }
    }
}
