package com.yandex.launcher.updaterapp;

import android.app.AlarmManager;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

import com.yandex.launcher.updaterapp.common.ApplicationConfig;
import com.yandex.launcher.updaterapp.core.Settings;
import com.yandex.launcher.updaterapp.core.configure.Configuration;
import com.yandex.launcher.updaterapp.notification.NotificationRemovedReceiver;

import org.junit.Test;
import org.robolectric.RuntimeEnvironment;
import org.robolectric.shadows.ShadowAlarmManager;
import org.robolectric.shadows.ShadowApplication;

import java.util.List;

import static junit.framework.Assert.assertEquals;
import static junit.framework.Assert.assertFalse;
import static junit.framework.Assert.assertTrue;

import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.when;
import static org.robolectric.Shadows.shadowOf;

public class BootReceiverTest extends BaseRobolectricTest {

    private static final Intent INTENT = new Intent(Intent.ACTION_BOOT_COMPLETED);

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

        assertEquals(1, ShadowApplication.getInstance().getReceiversForIntent(INTENT).size());
    }

    @Test
    public void shouldScheduleCheckOnReceiveIfEnabled() {
        final AlarmManager alarmManager = (AlarmManager) RuntimeEnvironment.application.getSystemService(Context.ALARM_SERVICE);
        final ShadowAlarmManager shadowAlarmManager = shadowOf(alarmManager);

        final Settings localSettings = new Settings(getApp());
        final Settings localSettingsSpy = spy(localSettings);

        localSettings.setUserAutoCheckEnabled(true);

        doReturn(true).when(localSettingsSpy).isAutoCheckEnabled();
        doReturn(true).when(settings).isAutoCheckEnabled();

        Configuration.Builder configBuilder = new Configuration.Builder(
                ApplicationConfig.getInstance(getApp()));

        configBuilder.setUpdateFrequencyJitterPercent(0);
        configBuilder.setAutoCheckEnabled(true);

        when(configurer.getCurrentConfiguration()).thenReturn(configBuilder.build());

        final BroadcastReceiver receiver = ShadowApplication.getInstance().getReceiversForIntent(INTENT).get(0);
        receiver.onReceive(getApp(), INTENT);

        assertEquals(1, shadowAlarmManager.getScheduledAlarms().size());
        final ShadowAlarmManager.ScheduledAlarm scheduledAlarm = shadowAlarmManager.getNextScheduledAlarm();
        assertEquals(AlarmManager.ELAPSED_REALTIME, scheduledAlarm.type);
    }

    @Test
    public void shouldNotScheduleCheckOnReceiveIfDisabled() {
        final AlarmManager alarmManager = (AlarmManager) RuntimeEnvironment.application.getSystemService(Context.ALARM_SERVICE);
        final ShadowAlarmManager shadowAlarmManager = shadowOf(alarmManager);

        final Settings settings = new Settings(getApp());
        settings.setUserAutoCheckEnabled(false);

        Configuration.Builder configBuilder = new Configuration.Builder(
                ApplicationConfig.getInstance(getApp()));

        configBuilder.setUpdateFrequencyJitterPercent(0);
        configBuilder.setAutoCheckEnabled(false);

        when(configurer.getCurrentConfiguration()).thenReturn(configBuilder.build());
        final BroadcastReceiver receiver = ShadowApplication.getInstance().getReceiversForIntent(INTENT).get(0);
        receiver.onReceive(getApp(), INTENT);

        assertTrue(shadowAlarmManager.getScheduledAlarms().isEmpty());
    }
}
