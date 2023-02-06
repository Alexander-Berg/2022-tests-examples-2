package com.yandex.launcher.updaterapp.download

import org.mockito.kotlin.*
import com.tonyodev.fetch2.Error
import com.tonyodev.fetch2.Status
import com.yandex.launcher.updaterapp.BaseRobolectricTest
import com.yandex.launcher.updaterapp.contract.models.Downloadable
import com.yandex.launcher.updaterapp.contract.models.Update
import com.yandex.launcher.updaterapp.core.install.Installer
import org.junit.Test
import org.mockito.ArgumentMatchers.anyLong
import org.mockito.ArgumentMatchers.contains
import org.mockito.Mockito.`when`

class DownloadHandlerTest : BaseRobolectricTest() {

    private val installer: Installer<Downloadable> = mock { }
    private val currentDownloads: CurrentDownloads = mock { }
    private lateinit var downloadHandler: DownloadHandler

    override fun setUp() {
        super.setUp()
        downloadHandler = DownloadHandler(installer, currentDownloads, updateContext)
    }

    @Test
    fun onDownloadComplete() {
        val downloadId = 1L

        val update = Update("app", "package", "http://some/url", "versionName", 1)
        val localPath = "/update.zip"
        update.localPath = localPath

        `when`(currentDownloads.getPackageName(downloadId)).thenReturn(update.packageName)
        `when`(updateItemsStorage.getItem(update.packageName)).thenReturn(update)
        `when`(settings.isAutoInstallEnabled(update)).thenReturn(true)

        downloadHandler.onDownloadCompleted(downloadId, Status.COMPLETED, Error.NONE, update.localPath)

        verify(installer, times(1)).install(update)
        verify(currentDownloads).removeDownload(downloadId)
        verify(metrica, only()).reportDownloadSuccess(update)
        verify(updateContext).onDownloaded(update, localPath)
        verifyNoInteractions(errorHandler)
    }

    @Test
    fun shouldNotInstallIfAutoInstallDisabled() {
        val downloadId = 1L

        val update = Update("app", "package", "http://some/url", "versionName", 1)
        val localPath = "/update.zip"
        update.localPath = localPath

        `when`(currentDownloads.getPackageName(downloadId)).thenReturn(update.packageName)
        `when`(updateItemsStorage.getItem(update.packageName)).thenReturn(update)
        `when`(settings.isAutoInstallEnabled(update)).thenReturn(false)

        downloadHandler.onDownloadCompleted(downloadId, Status.COMPLETED, Error.NONE, update.localPath)

        verifyNoInteractions(installer)
        verify(currentDownloads).removeDownload(downloadId)
        verify(metrica, only()).reportDownloadSuccess(update)
        verifyNoInteractions(errorHandler)
    }

    @Test
    fun onDownloadFailure() {
        val downloadId = 1L
        val status = Status.FAILED
        val localPath = "/update.zip"
        val packageName = "packageName"
        val update = Update("appName", packageName, "downloadUrl", "versionName", 1)
        `when`((updateItemsStorage.getItem(packageName))).thenReturn(update)

        `when`(currentDownloads.getPackageName(downloadId)).thenReturn(packageName)

        downloadHandler.onDownloadCompleted(downloadId, status, Error.NONE, localPath)

        verifyNoInteractions(installer)
        verify(currentDownloads).removeDownload(downloadId)

        val expectedMessage = ("Update download failed with status ${status.name}(${Error.NONE.name})")
        verify(metrica).reportDownloadFailure(update, expectedMessage)
        verify(errorHandler).onDownloadError(update, expectedMessage, Error.NONE.toUpdaterErrorCode())
    }

    @Test
    fun onUnknownDownloadComplete() {
        val status = Status.COMPLETED
        val localPath = "/update.zip"

        `when`(currentDownloads.getPackageName(anyLong())).thenReturn("")

        downloadHandler.onDownloadCompleted(1, status, Error.NONE, localPath)

        verifyNoInteractions(installer)
        verifyNoInteractions(metrica)
        verify(errorHandler).onDownloadError(isNull(), contains("FAILED(DOWNLOAD_NOT_FOUND)"), eq(Error.UNKNOWN.toUpdaterErrorCode()))
    }
}
