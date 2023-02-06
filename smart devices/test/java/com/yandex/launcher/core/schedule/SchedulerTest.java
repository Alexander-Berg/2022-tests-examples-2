package com.yandex.launcher.core.schedule;

import static junit.framework.TestCase.assertEquals;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static org.robolectric.Shadows.shadowOf;

import android.app.AlarmManager;
import android.content.Context;

import com.yandex.launcher.updaterapp.BaseRobolectricTest;
import com.yandex.launcher.updaterapp.common.UpdaterAction;
import com.yandex.launcher.updaterapp.core.schedule.Schedule;
import com.yandex.launcher.updaterapp.core.schedule.Scheduler;

import org.hamcrest.core.Is;
import org.junit.Test;
import org.robolectric.shadows.ShadowAlarmManager;
import org.robolectric.shadows.ShadowPendingIntent;

import java.util.List;

public class SchedulerTest extends BaseRobolectricTest {

    @Test
    public void shouldScheduleUpdate() {
        final long time = 123;

        final Schedule schedule = mock(Schedule.class);
        when(schedule.getNextCheckTime()).thenReturn(time);

        new Scheduler(getApp(), getSystemInfoProvider(), schedule).scheduleUpdateCheck();

        checkScheduledAlarms(time, UpdaterAction.CheckDownloadAndInstall);
    }

    @Test
    public void shouldScheduleNightInstall() {
        final long time = 999;

        final Schedule schedule = mock(Schedule.class);
        when(schedule.getNightInstallTime()).thenReturn(time);

        new Scheduler(getApp(), getSystemInfoProvider(), schedule).scheduleNightInstall();

        checkScheduledAlarms(time, UpdaterAction.InstallOnly);
    }

    private void checkScheduledAlarms(long expectedTime, UpdaterAction expectedAction) {
        final ShadowAlarmManager alarmManager = shadowOf((AlarmManager) getApp().getSystemService(Context.ALARM_SERVICE));

        final List<ShadowAlarmManager.ScheduledAlarm> alarms = alarmManager.getScheduledAlarms();

        assertThat(alarms.size(), Is.is(1));

        final ShadowAlarmManager.ScheduledAlarm alarm = alarms.get(0);
        assertEquals(expectedTime, alarm.triggerAtTime);

        final ShadowPendingIntent pendingIntent = shadowOf(alarm.operation);
        assertThat(pendingIntent.isForegroundServiceIntent(), Is.is(true));
    }
}
