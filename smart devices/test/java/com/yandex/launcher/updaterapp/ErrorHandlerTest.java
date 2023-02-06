package com.yandex.launcher.updaterapp;

import android.graphics.Bitmap;

import com.yandex.launcher.updaterapp.core.ErrorHandler;
import com.yandex.launcher.updaterapp.core.configure.Configuration;
import com.yandex.launcher.updaterapp.contract.models.Update;
import com.yandex.launcher.updaterapp.core.notification.constants.ErrorCode;

import org.junit.Test;
import org.mockito.Mockito;

import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.any;
import static org.mockito.Mockito.anyInt;

public class ErrorHandlerTest extends BaseRobolectricTest {

    // check for updates

    @Test
    public void shouldNotNotifyCheckForUpdatesErrorIfNoneNotificationsEnabled() {
        when(getSettings().getNotificationMode()).thenReturn(Configuration.NOTIFICATION_NONE);
        new ErrorHandler(getNotifier()).onCheckForUpdatesError("log message");
        verify(getNotifier(), times(1)).onCheckForUpdatesError(any(), eq(ErrorCode.CHECK_FOR_UPDATES_ERROR));
        verify(getNotifier(), times(0)).showDebugErrorNotification(any());
    }

    @Test
    public void shouldNotNotifyCheckForUpdatesErrorIfUserNotificationsEnabled() {
        when(getSettings().getNotificationMode()).thenReturn(Configuration.NOTIFICATION_RESULTS_ONLY);
        new ErrorHandler(getNotifier()).onCheckForUpdatesError("log message");
        verify(getNotifier(), times(1)).onCheckForUpdatesError(any(), eq(ErrorCode.CHECK_FOR_UPDATES_ERROR));
        verify(getNotifier(), times(0)).showDebugErrorNotification(any());
    }

    @Test
    public void shouldNotifyCheckForUpdatesIfAllNotificationsEnabled() {
        when(getSettings().getNotificationMode()).thenReturn(Configuration.NOTIFICATION_ALL);
        final Update update = new Update("message", "package", "app", "url", 1);
        new ErrorHandler(getNotifier()).onCheckForUpdatesError("log message");

        verify(getNotifier(), times(1)).onCheckForUpdatesError(any(), eq(ErrorCode.CHECK_FOR_UPDATES_ERROR));
        verify(getNotifier(), times(1)).showDebugErrorNotification(any());
    }

    // download

    @Test
    public void shouldNotNotifyDownloadErrorIfNoneNotificationsEnabled() {
        when(getSettings().getNotificationMode()).thenReturn(Configuration.NOTIFICATION_NONE);
        final Update update = new Update("message", "package", "app", "url", 1);
        new ErrorHandler(getNotifier()).onDownloadError(update, "message", ErrorCode.UNKNOWN);
        verify(getNotifier(), times(1)).onDownloadError(any(Update.class), any(), eq(ErrorCode.UNKNOWN));
        verify(getNotifier(), times(0)).showDebugErrorNotification(any());
    }

    @Test
    public void shouldNotNotifyDownloadErrorIfUserNotificationsEnabled() {
        when(getSettings().getNotificationMode()).thenReturn(Configuration.NOTIFICATION_RESULTS_ONLY);
        final Update update = new Update("message", "package", "app", "url", 1);
        new ErrorHandler(getNotifier()).onDownloadError(update, "message", ErrorCode.NETWORK_UNAVAILABLE);
        verify(getNotifier(), times(1)).onDownloadError(any(Update.class), any(), eq(ErrorCode.NETWORK_UNAVAILABLE));
        verify(getNotifier(), times(0)).showDebugErrorNotification(any());
    }

    @Test
    public void shouldNotifyDownloadErrorIfAllNotificationsEnabled() {
        when(getSettings().getNotificationMode()).thenReturn(Configuration.NOTIFICATION_ALL);
        final Update update = new Update("message", "package", "app", "url", 1);
        new ErrorHandler(getNotifier()).onDownloadError(update, "message", ErrorCode.NETWORK_UNAVAILABLE);
        verify(getNotifier(), times(1)).onDownloadError(any(Update.class), any(), eq(ErrorCode.NETWORK_UNAVAILABLE));
        verify(getNotifier(), times(1)).showDebugErrorNotification(any());
    }

    // invalid package

    @Test
    public void shouldNotNotifyInvalidPackageErrorIfNoneNotificationsEnabled() {
        when(getSettings().getNotificationMode()).thenReturn(Configuration.NOTIFICATION_NONE);
        final Update update = new Update("appName", "packageName", "downloadUrl", "versionName", 1);
        new ErrorHandler(getNotifier()).onInvalidPackageError(update, "message");
        verify(getNotifier(), times(1)).onInstallError(any(Update.class), any(), anyInt());
        verify(getNotifier(), times(0)).showDebugErrorNotification(any());
    }

    @Test
    public void shouldNotNotifyInvalidPackageErrorIfUserNotificationsEnabled() {
        final Update update = new Update("appName", "packageName", "downloadUrl", "versionName", 1);
        when(getSettings().getNotificationMode()).thenReturn(Configuration.NOTIFICATION_RESULTS_ONLY);
        new ErrorHandler(getNotifier()).onInvalidPackageError(update, "message");
        verify(getNotifier(), times(1)).onInstallError(any(Update.class), any(), anyInt());
        verify(getNotifier(), times(0)).showDebugErrorNotification(any());
    }

    @Test
    public void shouldNotifyInvalidPackageErrorIfAllNotificationsEnabled() {
        when(getSettings().getNotificationMode()).thenReturn(Configuration.NOTIFICATION_ALL);
        final Update update = new Update("appName", "packageName", "downloadUrl", "versionName", 1);
        new ErrorHandler(getNotifier()).onInvalidPackageError(update, "message");
        verify(getNotifier(), times(1)).onInstallError(any(Update.class), any(), anyInt());
        verify(getNotifier(), times(1)).showDebugErrorNotification(any());
    }

    // install

    @Test
    public void shouldNotNotifyInstallErrorIfNoneNotificationsEnabled() {
        when(getSettings().getNotificationMode()).thenReturn(Configuration.NOTIFICATION_NONE);
        final int errorCode = 33;
        Bitmap bitmap = Bitmap.createBitmap(100, 100, Bitmap.Config.ARGB_8888);
        final Update update = new Update("appName", "packageName", "downloadUrl", "versionName", 1);
        new ErrorHandler(getNotifier()).onInstallError(update, "log message", bitmap, errorCode);
        verify(getNotifier(), times(1)).onUpdateError(Mockito.any(Update.class), any(Bitmap.class), anyInt());
        verify(getNotifier(), times(0)).showUpdateFailureNotification(any(), any(Bitmap.class), anyInt());
    }

    @Test
    public void shouldNotifyInstallErrorIfUserNotificationsEnabled() {
        when(getSettings().getNotificationMode()).thenReturn(Configuration.NOTIFICATION_RESULTS_ONLY);
        final int errorCode = 33;
        Bitmap bitmap = Bitmap.createBitmap(100, 100, Bitmap.Config.ARGB_8888);
        final Update update = new Update("appName", "packageName", "downloadUrl", "versionName", 1);
        new ErrorHandler(getNotifier()).onInstallError(update, "log message", bitmap, errorCode);
        verify(getNotifier(), times(1)).onUpdateError(Mockito.any(Update.class), any(Bitmap.class), anyInt());
        verify(getNotifier(), times(1)).showUpdateFailureNotification(any(), any(Bitmap.class), anyInt());
    }

    @Test
    public void shouldNotifyInstallErrorIfAllNotificationsEnabled() {
        when(getSettings().getNotificationMode()).thenReturn(Configuration.NOTIFICATION_ALL);
        final int errorCode = 33;
        Bitmap bitmap = Bitmap.createBitmap(100, 100, Bitmap.Config.ARGB_8888);
        final Update update = new Update("appName", "packageName", "downloadUrl", "versionName", 1);
        new ErrorHandler(getNotifier()).onInstallError(update, "log message", bitmap, errorCode);
        verify(getNotifier(), times(1)).onUpdateError(Mockito.any(Update.class), any(Bitmap.class), anyInt());
        verify(getNotifier(), times(1)).showUpdateFailureNotification(any(), any(Bitmap.class), anyInt());
    }

}
