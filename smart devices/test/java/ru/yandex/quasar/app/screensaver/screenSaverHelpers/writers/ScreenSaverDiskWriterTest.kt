package ru.yandex.quasar.app.screensaver.screenSaverHelpers.writers

import android.content.Context
import android.content.SharedPreferences
import android.os.Environment
import android.os.StatFs
import com.google.gson.Gson
import com.google.gson.GsonBuilder
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.ArgumentMatchers
import org.mockito.kotlin.any
import org.mockito.kotlin.eq
import org.mockito.kotlin.inOrder
import org.mockito.kotlin.mock
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.powermock.api.mockito.PowerMockito
import org.powermock.core.classloader.annotations.PrepareForTest
import org.powermock.modules.junit4.PowerMockRunner
import ru.yandex.quasar.core.MetricaReporter
import ru.yandex.quasar.app.configs.ScreenSaverSystemConfig
import ru.yandex.quasar.app.configs.StationConfig
import ru.yandex.quasar.app.configs.SystemConfig
import ru.yandex.quasar.app.screensaver.screenSaverHelpers.ScreenSaverItemGsonConverter
import ru.yandex.quasar.app.screensaver.screenSaverItems.ScreenSaverItem
import java.io.File

@RunWith(PowerMockRunner::class)
@PrepareForTest(ScreenSaverDiskWriter::class, Environment::class)
class ScreenSaverDiskWriterTest {
    private val context: Context = mock()
    private val sharedPrefs: SharedPreferences = mock()
    private val config: StationConfig = mock()
    private val screenSaverGson: Gson
    private val metricaReporter: MetricaReporter = mock()
    private val screenSaverFolder: File = mock()

    init {
        val simpleGson = GsonBuilder().serializeNulls().create()
        screenSaverGson = GsonBuilder()
            .registerTypeHierarchyAdapter(
                ScreenSaverItem::class.java,
                ScreenSaverItemGsonConverter(simpleGson)
            )
            .serializeNulls()
            .create()
    }

    @Before
    fun setUp() {
        whenever(context.getSharedPreferences(any(), any())).thenReturn(sharedPrefs)

        val cacheDir: File = mock()
        whenever(context.cacheDir).thenReturn(cacheDir)
        whenever(cacheDir.path).thenReturn("testFolder")

        val systemConfig: SystemConfig = mock()
        val screenSaverConfig: ScreenSaverSystemConfig = mock()
        whenever(config.systemConfig).thenReturn(systemConfig)
        whenever(systemConfig.screenSaverConfig).thenReturn(screenSaverConfig)
        whenever(screenSaverConfig.writerMaxMemoryUse).thenReturn((245 * 1024 * 1024 + 1000).toLong())

        // return screenSaverFolder every time we creates testFolder
        PowerMockito.whenNew(File::class.java)
            .withArguments(ArgumentMatchers.matches("testFolder.*"))
            .thenReturn(screenSaverFolder)
    }

    @Test
    fun given_screenSaverFolderDoesNotExists_when_createDiskWriter_then_createFolder() {
        // screen saver folder doesn't exists and will be create successfully
        whenever(screenSaverFolder.exists()).thenReturn(false)
        whenever(screenSaverFolder.mkdir()).thenReturn(true)

        // create disk writer
        ScreenSaverDiskWriter(context, config, screenSaverGson, metricaReporter)

        // folder has to be created
        inOrder(screenSaverFolder) {
            verify(screenSaverFolder).exists()
            verify(screenSaverFolder).mkdir()
        }
    }

    @Test
    fun given_filesInScreenSaverFolder_when_restoreState_then_deleteFile() {
        // create file that saved in screen saver folder
        val savedFile: File = mock()
        whenever(savedFile.path).thenReturn("testFile")
        whenever(savedFile.delete()).thenReturn(true)
        PowerMockito.whenNew(File::class.java).withArguments(eq("testFile")).thenReturn(savedFile)
        whenever(screenSaverFolder.exists()).thenReturn(true)
        whenever(screenSaverFolder.listFiles()).thenReturn(arrayOf(savedFile))

        // create disk writer
        ScreenSaverDiskWriter(context, config, screenSaverGson, metricaReporter)

        // file has to be deleted
        verify(savedFile).delete()
    }


    @Test
    fun given_availableMemory_when_testNewItemCanBeLoaded() {
        // hack to avoid restoreState call
        whenever(screenSaverFolder.exists()).thenReturn(false)
        whenever(screenSaverFolder.mkdir()).thenReturn(true)

        // mock available memory (245Мб for system + 500B for new item)
        val stats: StatFs = mock()
        PowerMockito.whenNew(StatFs::class.java).withAnyArguments().thenReturn(stats)
        whenever(stats.availableBlocksLong).thenReturn(1)
        whenever(stats.blockSizeLong).thenReturn((245 * 1024 * 1024 + 500).toLong())

        // create diskWriter
        val diskWriter = ScreenSaverDiskWriter(context, config, screenSaverGson, metricaReporter, mock())

        // check we can or can't load new item
        assertFalse(diskWriter.canLoadNewMediaItem(5000))
        assertFalse(diskWriter.canLoadNewMediaItem(1000))
        assertFalse(diskWriter.canLoadNewMediaItem(700))
        assertTrue(diskWriter.canLoadNewMediaItem(500))
        assertTrue(diskWriter.canLoadNewMediaItem(200))
        assertTrue(diskWriter.canLoadNewMediaItem(0))
    }
}
