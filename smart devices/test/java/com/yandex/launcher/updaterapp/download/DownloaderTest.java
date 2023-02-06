package com.yandex.launcher.updaterapp.download;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import android.content.Context;

import com.yandex.launcher.updaterapp.BaseRobolectricTest;
import com.yandex.launcher.updaterapp.contract.models.Update;
import com.tonyodev.fetch2.Request;
import com.yandex.launcher.updaterapp.core.download.DownloadDirectory;

import org.junit.Before;
import org.junit.Test;

import java.io.IOException;

public class DownloaderTest extends BaseRobolectricTest {

    private Downloader downloader;
    private Downloader downloaderSpy;

    @Override
    @Before
    public void setUp() throws Exception {
        super.setUp();
        downloader = new Downloader();
        downloaderSpy = spy(downloader);
    }

    @Test
    public void shouldStartDownload() throws IOException {
        final DownloadDirectory downloadDirectory = new DownloadDirectory(getApp(), "test", "test");
        when(getUpdateContext().getDownloadDirectory()).thenReturn(downloadDirectory);

        final Update update = new Update("app", "package", "http://some/url", "versionName", 1);

        downloaderSpy.startDownload(getUpdateContext(), update);
        verify(downloaderSpy).startDownloadService(any(Context.class), any(Request.class));
    }

    @Test
    public void shouldStartDownloadForced() throws IOException {
        final DownloadDirectory downloadDirectory = new DownloadDirectory(getApp(), "test", "test");
        when(getUpdateContext().getDownloadDirectory()).thenReturn(downloadDirectory);

        final Update update = new Update("app", "package", "http://some/url", "versionName", 1);

        downloaderSpy.startDownloadForced(getUpdateContext(), update);
        verify(downloaderSpy).startDownloadService(any(Context.class), any(Request.class));
    }

    @Test
    public void shouldSkipDownloadIfUpdateHasLocalPath() throws IOException {
        final Update update = new Update("app", "package", "http://some/url", "versionName", 1);
        update.setLocalPath("/local/path");

        downloaderSpy.startDownload(getUpdateContext(), update);

        verifyDownloadSkipped();
    }

    /**
     * ********** Private methods **********
     */

    private void verifyDownloadSkipped() {
        verify(downloaderSpy, never()).startDownloadService(any(Context.class), any(Request.class));
    }
}
