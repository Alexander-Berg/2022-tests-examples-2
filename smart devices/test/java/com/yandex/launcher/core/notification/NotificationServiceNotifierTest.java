package com.yandex.launcher.core.notification;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.robolectric.Shadows.shadowOf;

import android.app.Notification;
import android.app.NotificationManager;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.os.Build;

import com.yandex.launcher.updaterapp.BaseRobolectricTest;
import com.yandex.launcher.updaterapp.R;
import com.yandex.launcher.updaterapp.core.Settings;
import com.yandex.launcher.updaterapp.contract.models.Update;
import com.yandex.launcher.updaterapp.core.configure.Configuration;
import com.yandex.launcher.updaterapp.core.notification.INotifier;
import com.yandex.launcher.updaterapp.core.notification.constants.NotificationIds;
import com.yandex.launcher.updaterapp.core.notification.NotificationServiceNotifier;
import com.yandex.launcher.updaterapp.ui.MainActivity;

import org.junit.Before;
import org.junit.Test;
import org.robolectric.shadows.ShadowNotification;
import org.robolectric.shadows.ShadowNotificationManager;
import org.robolectric.shadows.ShadowPendingIntent;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Locale;

public class NotificationServiceNotifierTest extends BaseRobolectricTest {

    private static final Bitmap APP_ICON = Bitmap.createBitmap(48, 48, Bitmap.Config.ARGB_8888);
    private static final String PACKAGE_NAME = "package.name";
    private static final String ACTIVITY_NAME = "Activity";
    private static final String APP_NAME = "appName";

    private PackageManager packageManager;

    private ShadowNotificationManager shadowNotificationManager;

    private Settings settings;

    private INotifier notifier;

    @Override
    @Before
    public void setUp() throws Exception {
        super.setUp();

        packageManager = mock(PackageManager.class);

        final Context context = spy(getApp());
        when(context.getPackageManager()).thenReturn(packageManager);

        when(getUpdateContext().getContext()).thenReturn(context);

        NotificationManager manager = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
        shadowNotificationManager = shadowOf(manager);

        settings = mock(Settings.class);

        notifier = new NotificationServiceNotifier(context, settings);

        APP_ICON.eraseColor(Color.argb(255, 255, 0, 0));
    }

    @Test
    public void shouldDisplayUpdateInProgressNotification() throws NoSuchFieldException {
        final Update update = new Update(APP_NAME, PACKAGE_NAME, "app", "url", 1);

        notifier.onUpdateInProgress(update, APP_ICON);

        checkNotifications(APP_NAME, APP_NAME + " updating…", R.drawable.notification_progress, true);
    }

    @Test
    public void shouldDisplayUpdateFailureNotification() throws NoSuchFieldException {
        when(settings.getNotificationMode()).thenReturn(Configuration.NOTIFICATION_RESULTS_ONLY);

        final int errorCode = 33;

        final Update update = new Update(APP_NAME, PACKAGE_NAME, "app", "url", 1);
        notifier.onUpdateInProgress(update, APP_ICON);
        notifier.onUpdateError(update, APP_ICON, errorCode);

        final String expectedText = String.format(Locale.getDefault(),
                getApp().getString(R.string.updater_notification_update_failure_format), errorCode);

        checkNotifications(APP_NAME, expectedText, R.drawable.notification_error, false);
    }

    @Test
    public void shouldDisplayUpdateSuccessNotificationOneApp() throws NoSuchFieldException {
        final List<String> previousApps = Collections.emptyList();

        final String expectedTitle = APP_NAME;
        final String expectedText = getApp().getString(R.string.updater_notification_update_success_text_one_app);

        shouldDisplayUpdateSuccessNotification(previousApps, expectedTitle, expectedText);
    }

    @Test
    public void shouldDisplayUpdateSuccessNotificationManyApps() throws NoSuchFieldException {
        final List<String> previousApps = Arrays.asList("prevAppName1", "prevAppName2", "prevAppName3");
        when(settings.getUpdatesNotifications()).thenReturn(previousApps);

        final String expectedTitle = String.format(Locale.ENGLISH, "%s and %d more", APP_NAME, previousApps.size());
        final String expectedText = getApp().getString(R.string.updater_notification_update_success_text_many_apps);

        shouldDisplayUpdateSuccessNotification(previousApps, expectedTitle, expectedText);
    }

    @Test
    public void shouldDisplayUpdateSuccessNotificationSameApps() throws NoSuchFieldException {
        final List<String> previousApps = new ArrayList<>();
        previousApps.add("appName");

        final String expectedTitle = APP_NAME;
        final String expectedText = getApp().getString(R.string.updater_notification_update_success_text_one_app);

        shouldDisplayUpdateSuccessNotification(previousApps, expectedTitle, expectedText);
    }

    @Test
    public void shouldDisplayUpdateAvailableNotificationOneApp() throws NoSuchFieldException {
        final List<String> previousApps = Collections.emptyList();

        final String expectedTitle = "[debug] " + APP_NAME;
        final String expectedText = "Update available";

        shouldDisplayUpdateAvailableNotification(previousApps, expectedTitle, expectedText);
    }

    @Test
    public void shouldDisplayUpdateAvailableNotificationManyApps() throws NoSuchFieldException {
        final List<String> previousApps = Arrays.asList("prevAppName1", "prevAppName2", "prevAppName3");
        when(settings.getUpdatesNotifications()).thenReturn(previousApps);

        final String expectedTitle = String.format(Locale.ENGLISH, "%s and %d more", APP_NAME, previousApps.size());
        final String expectedText = "Updates available";

        shouldDisplayUpdateAvailableNotification(previousApps, expectedTitle, expectedText);
    }

    @Test
    public void shouldDisplayUpdateAvailableNotificationSameApps() throws NoSuchFieldException {
        final List<String> previousApps = new ArrayList<>();
        previousApps.add("appName");

        final String expectedTitle = "[debug] " + APP_NAME;
        final String expectedText = "Update available";

        shouldDisplayUpdateAvailableNotification(previousApps, expectedTitle, expectedText);
    }

    @Test
    public void shouldHideUpdateAvailableNotifications() {
        final Update update = new Update(APP_NAME, PACKAGE_NAME, "http://some/url", "versionName", 1);

        notifier.onUpdateAvailable(update, APP_ICON, MainActivity.class);
        assertEquals(1, shadowNotificationManager.getAllNotifications().size());

        notifier.cancelNotification(NotificationIds.DEBUG_UPDATE_AVAILABLE_ID);
        assertEquals(0, shadowNotificationManager.getAllNotifications().size());
    }

    /**
     * ********** Private Methods **********
     */

    private void shouldDisplayUpdateSuccessNotification(List<String> previousApps, String expectedTitle, String expectedText) {
        when(settings.getUpdatesNotifications()).thenReturn(previousApps);

        final Intent contentIntent = new Intent(Intent.ACTION_MAIN);
        contentIntent.setClassName(PACKAGE_NAME, ACTIVITY_NAME);
        when(packageManager.getLaunchIntentForPackage(PACKAGE_NAME)).thenReturn(contentIntent);

        final Intent deleteIntent = new Intent(INotifier.NOTIFICATION_REMOVED_ACTION);
        deleteIntent.putExtra(INotifier.NOTIFICATION_ID_EXTRA, NotificationIds.UPDATE_SUCCESS_ID);

        final Update update = new Update(APP_NAME, PACKAGE_NAME, "app", "url", 1);
        notifier.onUpdated(update, APP_ICON);

        checkNotifications(expectedTitle, expectedText, R.drawable.notification_success, false, contentIntent, deleteIntent);

        verify(settings).addUpdateNotification(APP_NAME);
    }

    private void shouldDisplayUpdateAvailableNotification(List<String> previousApps, String expectedTitle, String expectedText) {
        when(settings.getUpdateAvailableNotifications()).thenReturn(previousApps);

        final Intent contentIntent = new Intent(getApp(), MainActivity.class);

        final Intent deleteIntent = new Intent(INotifier.NOTIFICATION_REMOVED_ACTION);
        deleteIntent.putExtra(INotifier.NOTIFICATION_ID_EXTRA, NotificationIds.DEBUG_UPDATE_AVAILABLE_ID);

        final Update update = new Update(APP_NAME, PACKAGE_NAME, "app", "url", 1);

        notifier.onUpdateInProgress(update, APP_ICON);
        notifier.onUpdateAvailable(update, APP_ICON, MainActivity.class);

        checkNotifications(expectedTitle, expectedText, R.drawable.notification_progress, false, contentIntent, deleteIntent);

        verify(settings).addUpdateAvailableNotification(APP_NAME);
    }

    private void checkNotifications(String expectedTitle, String expectedText, int smallIconResId, boolean isOngoing) {
        checkNotifications(expectedTitle, expectedText, smallIconResId, isOngoing, null, null);
    }

    @SuppressWarnings("deprecation")
    private void checkNotifications(String expectedTitle, String expectedText, int smallIconResId, boolean isOngoing,
                                    Intent contentIntent, Intent deleteIntent) {
        final List<Notification> notifications = shadowNotificationManager.getAllNotifications();
        assertEquals(1, notifications.size());
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {
            final ShadowNotification notification = shadowOf(notifications.get(0));
            final Notification realNotification = notifications.get(0);

            assertEquals(expectedTitle, notification.getContentTitle());
            assertEquals(expectedText, notification.getContentText());
            assertEquals(isOngoing, notification.isOngoing());

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                assertEquals(APP_ICON, shadowOf(realNotification.getLargeIcon()).getBitmap());
            } else {
                assertEquals(APP_ICON, realNotification.largeIcon);
            }
            assertEquals(smallIconResId, realNotification.icon);

            if (contentIntent != null) {
                final ShadowPendingIntent pendingIntent = shadowOf(realNotification.contentIntent);
                assertTrue(pendingIntent.isActivityIntent());
                final Intent savedIntent = pendingIntent.getSavedIntent();

                assertEquals(contentIntent.getComponent(), savedIntent.getComponent());
                assertEquals(contentIntent.getAction(), savedIntent.getAction());
                assertEquals(contentIntent.getExtras(), savedIntent.getExtras());
            }

            if (deleteIntent != null) {
                final ShadowPendingIntent pendingIntent = shadowOf(realNotification.deleteIntent);
                assertTrue(pendingIntent.isBroadcastIntent());
                final Intent savedIntent = pendingIntent.getSavedIntent();

                assertEquals(deleteIntent.getComponent(), savedIntent.getComponent());
                assertEquals(deleteIntent.getAction(), savedIntent.getAction());
                assertEquals(deleteIntent.getExtras().size(), savedIntent.getExtras().size());
                assertEquals(deleteIntent.getExtras().get(INotifier.NOTIFICATION_ID_EXTRA),
                        savedIntent.getExtras().get(INotifier.NOTIFICATION_ID_EXTRA));
            }
        }
    }
}
