package com.yandex.launcher.updaterapp.download;

import android.os.Environment;
import android.text.TextUtils;

import com.yandex.launcher.updaterapp.BaseRobolectricTest;

import junit.framework.Assert;

import org.junit.Before;
import org.junit.Test;

import java.util.List;

public class CurrentDownloadsTest extends BaseRobolectricTest {

    private static final long DOWNLOAD_ID_1 = 1;
    private static final String PACKAGE_NAME_1 = "some.package1";
    private static final String LOCAL_PATH_1 = Environment.getDownloadCacheDirectory() + "/some.package1.apk";
    private static final String DOWNLOAD_URL_1 = "download_url1";

    private static final long DOWNLOAD_ID_2 = 2;
    private static final String PACKAGE_NAME_2 = "some.package2";
    private static final String LOCAL_PATH_2 = Environment.getDownloadCacheDirectory() + "/some.package2.apk";
    private static final String DOWNLOAD_URL_2 = "download_url2";

    private static final int DOWNLOAD_ID_3 = 3;

    @Override
    @Before
    public void setUp() throws Exception {
        super.setUp();
        CurrentDownloads currentDownloads = new CurrentDownloads(getApp());
        currentDownloads.clear();
        currentDownloads.addDownload(DOWNLOAD_ID_1, PACKAGE_NAME_1, LOCAL_PATH_1, DOWNLOAD_URL_1);
        currentDownloads.addDownload(DOWNLOAD_ID_2, PACKAGE_NAME_2, LOCAL_PATH_2, DOWNLOAD_URL_2);
    }

    @Test
    public void getPackageName() {
        final CurrentDownloads currentDownloads = new CurrentDownloads(getApp());
        Assert.assertEquals(PACKAGE_NAME_1, currentDownloads.getPackageName(DOWNLOAD_ID_1));
        Assert.assertEquals(PACKAGE_NAME_2, currentDownloads.getPackageName(DOWNLOAD_ID_2));
    }

    @Test
    public void removeDownload() {
        CurrentDownloads currentDownloads = new CurrentDownloads(getApp());
        currentDownloads.removeDownload(DOWNLOAD_ID_1);

        currentDownloads = new CurrentDownloads(getApp());
        Assert.assertTrue(TextUtils.isEmpty(currentDownloads.getPackageName(DOWNLOAD_ID_1)));
        Assert.assertEquals(PACKAGE_NAME_2, currentDownloads.getPackageName(DOWNLOAD_ID_2));
    }

    @Test
    public void getDownloadsFilterByPackageNameReturnSingleResult() {
        CurrentDownloads currentDownloads = new CurrentDownloads(getApp());

        boolean requestPackageFound = false;
        boolean otherPackagesFound = false;

        List<CurrentDownloads.DownloadInfo> downloads = currentDownloads.getDownloads(PACKAGE_NAME_1, null);

        for (CurrentDownloads.DownloadInfo download : downloads) {
            if (download.packageName.equals(PACKAGE_NAME_1)) {
                requestPackageFound = true;
            } else {
                otherPackagesFound = true;
            }
        }

        Assert.assertTrue(requestPackageFound && !otherPackagesFound);
        Assert.assertEquals(1, downloads.size());
    }

    @Test
    public void attemptsIncreasedByOneOnAddDownload() {
        CurrentDownloads currentDownloads = new CurrentDownloads(getApp());

        int initialAttempts = currentDownloads.getDownloads(PACKAGE_NAME_2, null).get(0).attempts;
        currentDownloads.addDownload(DOWNLOAD_ID_2, PACKAGE_NAME_2, LOCAL_PATH_2, DOWNLOAD_URL_2);

        int newAttempts = currentDownloads.getDownloads(PACKAGE_NAME_2, null).get(0).attempts;

        int delta = newAttempts - initialAttempts;

        Assert.assertEquals(1, delta);
    }

    @Test
    public void attemptsStartsFromOneInAddDownload() {
        CurrentDownloads currentDownloads = new CurrentDownloads(getApp());
        currentDownloads.clear();

        currentDownloads.addDownload(DOWNLOAD_ID_2, PACKAGE_NAME_2, LOCAL_PATH_2, DOWNLOAD_URL_2);

        int attempts = currentDownloads.getDownloads(PACKAGE_NAME_2, null).get(0).attempts;

        Assert.assertEquals(1, attempts);
    }

    @Test
    public void getDownloadsFilterByDownloadUrlReturnSingleResult() {
        CurrentDownloads currentDownloads = new CurrentDownloads(getApp());

        currentDownloads.addDownload(DOWNLOAD_ID_3, PACKAGE_NAME_1, LOCAL_PATH_1, DOWNLOAD_URL_1 + "_second");

        boolean requestDownloadUrlFound = false;
        boolean otherDownloadUrlsFound = false;

        List<CurrentDownloads.DownloadInfo> downloads = currentDownloads.getDownloads(PACKAGE_NAME_1, DOWNLOAD_URL_1);

        for (CurrentDownloads.DownloadInfo download : downloads) {
            if (DOWNLOAD_URL_1.equals(download.downloadUrl)) {
                requestDownloadUrlFound = true;
            } else {
                otherDownloadUrlsFound = true;
            }
        }

        Assert.assertTrue(requestDownloadUrlFound && !otherDownloadUrlsFound);
        Assert.assertEquals(1, downloads.size());
    }

    @Test
    public void getDownloadsFilterByPackageNameReturnMultipleResult() {
        CurrentDownloads currentDownloads = new CurrentDownloads(getApp());

        currentDownloads.addDownload(DOWNLOAD_ID_3, PACKAGE_NAME_1, LOCAL_PATH_1, DOWNLOAD_URL_1 + "_second");

        boolean requestPackageFound = false;
        boolean otherPackagesFound = false;

        List<CurrentDownloads.DownloadInfo> downloads = currentDownloads.getDownloads(PACKAGE_NAME_1, null);

        for (CurrentDownloads.DownloadInfo download : downloads) {
            if (download.packageName.equals(PACKAGE_NAME_1)) {
                requestPackageFound = true;
            } else {
                otherPackagesFound = true;
            }
        }

        Assert.assertTrue(requestPackageFound && !otherPackagesFound);
        Assert.assertEquals(2, downloads.size());
    }
}
