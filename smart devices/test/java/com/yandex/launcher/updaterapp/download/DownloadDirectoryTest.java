package com.yandex.launcher.updaterapp.download;

import com.yandex.launcher.updaterapp.BaseRobolectricTest;
import com.yandex.launcher.updaterapp.core.download.DownloadDirectory;

import junit.framework.Assert;

import org.junit.Test;

import java.io.File;
import java.io.IOException;
import java.util.Arrays;

public class DownloadDirectoryTest extends BaseRobolectricTest {

    @Test
    public void shouldPurge() throws IOException {
        final DownloadDirectory dir = new DownloadDirectory(getApp(), "updates", "upd");
        final File file1 = dir.createFile();
        final File file2 = dir.createFile();
        final File file3 = dir.createFile();
        dir.purge(getApp(), Arrays.asList(file1.getAbsolutePath(), file2.getAbsolutePath()));
        Assert.assertTrue(file1.exists());
        Assert.assertTrue(file2.exists());
        Assert.assertFalse(file3.exists());

        final File[] files = file3.getParentFile().listFiles();
        Assert.assertEquals(2, files.length);
    }
}
