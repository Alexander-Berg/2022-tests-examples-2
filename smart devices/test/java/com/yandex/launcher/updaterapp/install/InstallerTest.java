package com.yandex.launcher.updaterapp.install;

import android.app.Application;
import android.content.Context;
import android.content.pm.IPackageInstallObserver;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.RemoteException;

import com.yandex.launcher.updaterapp.BaseRobolectricTest;
import com.yandex.launcher.updaterapp.StubPackageManager;
import com.yandex.launcher.updaterapp.common.ApplicationConfig;
import com.yandex.launcher.updaterapp.core.configure.Configuration;
import com.yandex.launcher.updaterapp.core.metrica.SessionIdProvider;
import com.yandex.launcher.updaterapp.core.SystemInfoProvider;
import com.yandex.launcher.updaterapp.contract.models.Update;
import com.yandex.launcher.updaterapp.core.install.ApkInstaller;

import org.junit.Test;

import java.io.File;
import java.io.IOException;

import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.ArgumentMatchers.contains;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.ArgumentMatchers.isNull;
import static org.mockito.Mockito.atMost;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.any;
import static org.robolectric.Shadows.shadowOf;

import androidx.test.core.app.ApplicationProvider;

public class InstallerTest extends BaseRobolectricTest {

    @Test
    public void packageFileNotFound() {
        final Update update = new Update("appName", "packageName", "downloadUrl", "versionName", 1);

        when(getSystemInfoProvider().isPackageInstalledAndEnabled(update.getPackageName()))
                .thenReturn(true);

        new ApkInstaller(getUpdateContext()).install(update, true);
        String sessionId = new SessionIdProvider(getUpdateContext().getContext(), getSystemInfoProvider()).getStoredAppSessionId();
        verify(getNotifier(), times(1)).onInstallStarted(any(Update.class));
        verify(getMetrica()).reportInstallStarted(update, sessionId);
        verify(getMetrica()).reportInstallFailure(contains("Package file not found"), eq(update.getPackageName()), eq(sessionId), isNull());
        verify(getErrorHandler()).onInvalidPackageError(eq(update), contains("Package file not found"));

        verify(getNotifier(), times(0)).onInstalled(any(Update.class), any(Bitmap.class));
    }

    @SuppressWarnings("ResultOfMethodCallIgnored")
    @Test
    public void cannotGetTopPackage() throws IOException {
        final Update update = new Update("appName", "packageName", "downloadUrl", "versionName", 2);

        File file = null;
        try {
            file = File.createTempFile("upd", null);
            update.setLocalPath(file.getAbsolutePath());

            shadowOf((Application) ApplicationProvider.getApplicationContext()).grantPermissions(android.Manifest.permission.INSTALL_PACKAGES);

            new ApkInstaller(getUpdateContext()).install(update, true);
            String sessionId = new SessionIdProvider(getUpdateContext().getContext(), getSystemInfoProvider()).getStoredAppSessionId();
            verify(getNotifier(), times(1)).onInstallStarted(any(Update.class));
            verify(getErrorHandler(), times(1)).onPackageNotInstalled(any(Update.class));

            verify(getScheduler(), never()).scheduleUpdateCheck();
            verify(getMetrica()).reportInstallStarted(update, sessionId);
            verify(getMetrica()).reportInstallFailure("Application packageName is not installed - update ignored",
                    update.getPackageName(),
                    sessionId,
                    null);
            verify(getNotifier(), times(0)).onInstalled(any(Update.class), any(Bitmap.class));
        } finally {
            if (file != null) {
                file.delete();
            }
        }
    }

    @SuppressWarnings("ResultOfMethodCallIgnored")
    @Test
    public void shouldScheduleNightInstallIfAppActiveAndNotNightNow() throws IOException {
        final Update update = new Update("appName", "packageName", "downloadUrl", "versionName", 2);

        final int originalVersion = 1;
        setupSystemInfoProvider(update.getPackageName(), update.getPackageName(), originalVersion, update.getVersionCode());

        File file = null;
        try {
            file = File.createTempFile("upd", null);
            update.setLocalPath(file.getAbsolutePath());

            when(getTimeUtils().isNowNightInstallPeriod(getSettings().getNightPeriodStartHour(), getSettings().getNightPeriodStartHour()))
                    .thenReturn(false);

            when(configurer.fetchConfiguration()).thenReturn(new Configuration.Builder(ApplicationConfig.getInstance(getApp())).build());

            shadowOf((Application) ApplicationProvider.getApplicationContext()).grantPermissions(android.Manifest.permission.INSTALL_PACKAGES);

            new ApkInstaller(getUpdateContext()).install(update, true);

            String sessionId = new SessionIdProvider(getUpdateContext().getContext(), getSystemInfoProvider()).getStoredAppSessionId();
            verify(getMetrica()).reportInstallCancel(update.getPackageName(), sessionId, true, "Application is in foreground state");
            verify(getScheduler()).scheduleNightInstall();
            verifyNoInteractions(getErrorHandler());
        } finally {
            if (file != null) {
                file.delete();
            }
        }
    }

    @SuppressWarnings("ResultOfMethodCallIgnored")
    @Test
    public void shouldNotScheduleNightInstallIfAppActiveAndNightNow() throws IOException {
        final Update update = new Update("appName", "packageName", "downloadUrl", "versionName", 2);

        setupSystemInfoProvider(update.getPackageName(), update.getPackageName(), 1, 2);

        File file = null;
        try {
            file = File.createTempFile("upd", null);
            update.setLocalPath(file.getAbsolutePath());

            when(getTimeUtils().isNowNightInstallPeriod(getSettings().getNightPeriodStartHour(), getSettings().getNightPeriodStartHour()))
                    .thenReturn(true);

            when(configurer.fetchConfiguration()).thenReturn(new Configuration.Builder(ApplicationConfig.getInstance(getApp())).build());

            shadowOf((Application) ApplicationProvider.getApplicationContext()).grantPermissions(android.Manifest.permission.INSTALL_PACKAGES);

            new ApkInstaller(getUpdateContext()).install(update, true);

            verify(getScheduler(), never()).scheduleNightInstall();
        } finally {
            if (file != null) {
                file.delete();
            }
        }
    }

    @SuppressWarnings("ResultOfMethodCallIgnored")
    @Test
    public void invalidPackage() throws IOException {
        final Update update = new Update("appName", "packageName", "downloadUrl", "versionName", 2);

        setupSystemInfoProvider(update.getPackageName(), "topPackageName", 1, SystemInfoProvider.INVALID_APP_VERSION);

        File file = null;
        try {
            file = File.createTempFile("upd", null);
            update.setLocalPath(file.getAbsolutePath());

            shadowOf((Application) ApplicationProvider.getApplicationContext()).grantPermissions(android.Manifest.permission.INSTALL_PACKAGES);

            new ApkInstaller(getUpdateContext()).install(update, true);

            verify(getNotifier(), times(1)).onInstallStarted(any(Update.class));

            final String expectedMessage = "Cannot read package version";
            String sessionId = new SessionIdProvider(getUpdateContext().getContext(), getSystemInfoProvider()).getStoredAppSessionId();
            verify(getMetrica()).reportInstallFailure(expectedMessage,
                    update.getPackageName(),
                    sessionId,
                    null);
            verify(getErrorHandler()).onInvalidPackageError(update, expectedMessage);

            verify(getNotifier(), times(0)).onInstalled(any(Update.class), any(Bitmap.class));
        } finally {
            if (file != null) {
                file.delete();
            }
        }
    }

    @SuppressWarnings({"ResultOfMethodCallIgnored", "unused"})
    @Test
    public void installationSuccess() throws Exception {
        final int originalVersion = 1;
        final Update update = new Update("appName", "packageName", "downloadUrl", "versionName", 2);

        setupSystemInfoProvider(update.getPackageName(), "topPackageName", originalVersion, update.getVersionCode());

        File file = null;
        try {
            file = File.createTempFile("upd", null);
            update.setLocalPath(file.getAbsolutePath());

            shadowOf((Application) ApplicationProvider.getApplicationContext()).grantPermissions(android.Manifest.permission.INSTALL_PACKAGES);

            final Context context = mock(Context.class);
            when(context.getApplicationContext())
                    .thenReturn(getApp());
            when(context.getPackageManager())
                    .thenReturn(new StubPackageManager() {
                        @Override
                        public void installPackage(Uri packageURI, IPackageInstallObserver observer,
                                                   int flags, String installerPackageName) throws RemoteException {
                            observer.packageInstalled(update.getPackageName(), 1); // PackageManager.INSTALL_SUCCEEDED
                        }
                    });
            when(getUpdateContext().getContext())
                    .thenReturn(context);
            when(configurer.fetchConfiguration()).thenReturn(new Configuration.Builder(ApplicationConfig.getInstance(getApp())).build());
            doReturn(null).when(getSystemInfoProvider()).getApkIcon(file.getAbsolutePath());

            new ApkInstaller(getUpdateContext()).install(update, true);

            verifyInstallSuccess(update);
        } finally {
            if (file != null) {
                file.delete();
            }
        }
    }

    @SuppressWarnings({"ResultOfMethodCallIgnored", "unused"})
    @Test
    public void installationFailure() throws Exception {
        final Update update = new Update("appName", "packageName", "downloadUrl", "versionName", 2);
        final int originalVersion = 1;
        final int resultCode = -2; // PackageManager.INSTALL_FAILED_ALREADY_EXISTS

        setupSystemInfoProvider(update.getPackageName(), "topPackageName", originalVersion, update.getVersionCode());

        File file = null;
        try {
            file = File.createTempFile("upd", null);
            update.setLocalPath(file.getAbsolutePath());

            shadowOf((Application) ApplicationProvider.getApplicationContext()).grantPermissions(android.Manifest.permission.INSTALL_PACKAGES);

            final Context context = mock(Context.class);
            when(context.getApplicationContext()).thenReturn(getApp());
            when(context.getPackageManager()).thenReturn(new StubPackageManager() {
                @Override
                public void installPackage(Uri packageURI, IPackageInstallObserver observer,
                                           int flags, String installerPackageName) throws RemoteException {
                    observer.packageInstalled(update.getPackageName(), resultCode);
                }
            });
            when(getUpdateContext().getContext()).thenReturn(context);
            when(configurer.fetchConfiguration()).thenReturn(new Configuration.Builder(ApplicationConfig.getInstance(getApp())).build());
            doReturn(null).when(getSystemInfoProvider()).getApkIcon(file.getAbsolutePath());

            new ApkInstaller(getUpdateContext()).install(update, true);

            final String expectedMessage = ApkInstaller.InstallStatus.INVALID_INPUT.getMessage() + "(" + resultCode + ")";
            String sessionId = new SessionIdProvider(getUpdateContext().getContext(), getSystemInfoProvider()).getStoredAppSessionId();
            verify(getErrorHandler()).onInstallError(update, expectedMessage, null, ApkInstaller.InstallStatus.INVALID_INPUT.convertToErrorCode());
            verify(getMetrica()).reportInstallFailure(expectedMessage, update.getPackageName(), sessionId, false);
        } finally {
            if (file != null) {
                file.delete();
            }
        }
    }

    /**
     * ********** Private methods **********
     */

    private void verifyInstallSuccess(Update update) {
        String sessionId = new SessionIdProvider(getUpdateContext().getContext(), getSystemInfoProvider()).getStoredAppSessionId();
        verify(getMetrica()).reportInstallStarted(update, sessionId);
        verify(getMetrica()).reportInstallSuccess(update.getPackageName(), sessionId, false);
        verify(getNotifier()).onUpdated(eq(update), isNull());
        verify(getScheduler(), atMost(1)).scheduleUpdateProgressCancel(anyLong());
        verifyNoInteractions(getErrorHandler());
    }

    private void setupSystemInfoProvider(String packageName, String topPackageName, long originalVersion, long updateVersion) {
        when(getSystemInfoProvider().getTopPackageName())
                .thenReturn(topPackageName);
        when(getSystemInfoProvider().getInstalledPackageVersionCode(any()))
                .thenReturn(originalVersion);
        when(getSystemInfoProvider().getApkVersion(any()))
                .thenReturn(updateVersion);
        when(getSystemInfoProvider().isPackageInstalledAndEnabled(packageName))
                .thenReturn(true);
        when(getSystemInfoProvider().isDeviceActive())
                .thenReturn(true);
        when(getSystemInfoProvider().hasAutoInstallPermission())
                .thenReturn(true);
    }
}
