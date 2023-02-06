package com.yandex.launcher.core.notification;

import android.content.BroadcastReceiver;
import android.content.Intent;

import com.yandex.launcher.updaterapp.BaseRobolectricTest;
import com.yandex.launcher.updaterapp.core.Settings;
import com.yandex.launcher.updaterapp.core.notification.INotifier;
import com.yandex.launcher.updaterapp.core.notification.constants.NotificationIds;
import com.yandex.launcher.updaterapp.notification.NotificationRemovedReceiver;

import org.junit.Test;
import org.robolectric.shadows.ShadowApplication;

import java.util.List;

import static junit.framework.TestCase.assertEquals;
import static junit.framework.TestCase.assertFalse;
import static junit.framework.TestCase.assertTrue;

public class NotificationRemovedReceiverTest extends BaseRobolectricTest {

    @Test
    public void receiverRegistered() {
        final List<ShadowApplication.Wrapper> registeredReceivers = ShadowApplication.getInstance().getRegisteredReceivers();
        assertFalse(registeredReceivers.isEmpty());
        boolean receiverFound = false;
        for (ShadowApplication.Wrapper wrapper : registeredReceivers) {
            if (!receiverFound)
                receiverFound = NotificationRemovedReceiver.class.getSimpleName().equals(
                        wrapper.broadcastReceiver.getClass().getSimpleName());
        }
        assertTrue(receiverFound);

        final Intent intent = new Intent(INotifier.NOTIFICATION_REMOVED_ACTION);
        assertEquals(1, ShadowApplication.getInstance().getReceiversForIntent(intent).size());
    }

    @Test
    public void shouldClearUpdatesNotifications() {
        final Intent intent = new Intent(INotifier.NOTIFICATION_REMOVED_ACTION);
        intent.putExtra(INotifier.NOTIFICATION_ID_EXTRA, NotificationIds.UPDATE_SUCCESS_ID);

        final Settings settings = new Settings(getApp());
        settings.addUpdateNotification("app1");
        settings.addUpdateNotification("app2");
        assertEquals(2, settings.getUpdatesNotifications().size());

        final BroadcastReceiver receiver = ShadowApplication.getInstance().getReceiversForIntent(intent).get(0);
        receiver.onReceive(getApp(), intent);

        assertTrue(settings.getUpdatesNotifications().isEmpty());
    }

    @Test
    public void shouldClearInstallsNotifications() {
        final Intent intent = new Intent(INotifier.NOTIFICATION_REMOVED_ACTION);
        intent.putExtra(INotifier.NOTIFICATION_ID_EXTRA, NotificationIds.INSTALL_SUCCESS_ID);

        final Settings settings = new Settings(getApp());
        settings.addInstallNotification("app1");
        settings.addInstallNotification("app2");
        assertEquals(2, settings.getInstallsNotifications().size());

        final BroadcastReceiver receiver = ShadowApplication.getInstance().getReceiversForIntent(intent).get(0);
        receiver.onReceive(getApp(), intent);

        assertTrue(settings.getInstallsNotifications().isEmpty());
    }

    @Test
    public void shouldClearUpdateAvailableNotifications() {
        final Intent intent = new Intent(INotifier.NOTIFICATION_REMOVED_ACTION);
        intent.putExtra(INotifier.NOTIFICATION_ID_EXTRA, NotificationIds.DEBUG_UPDATE_AVAILABLE_ID);

        final Settings settings = new Settings(getApp());
        settings.addUpdateAvailableNotification("app1");
        settings.addUpdateAvailableNotification("app2");
        assertEquals(2, settings.getUpdateAvailableNotifications().size());

        final BroadcastReceiver receiver = ShadowApplication.getInstance().getReceiversForIntent(intent).get(0);
        receiver.onReceive(getApp(), intent);

        assertTrue(settings.getUpdateAvailableNotifications().isEmpty());
    }
}
