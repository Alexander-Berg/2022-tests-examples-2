package com.yandex.launcher.core.schedule;

import android.os.SystemClock;

import com.yandex.launcher.updaterapp.BaseRobolectricTest;
import com.yandex.launcher.updaterapp.core.schedule.Schedule;

import junit.framework.Assert;

import org.junit.Test;

import java.util.concurrent.TimeUnit;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.mockito.Mockito.when;

public class ScheduleTest extends BaseRobolectricTest {

    @Test
    public void getNextCheckTimeWithoutPreviousCheck() {
        when(getSettings().getLastCheckTimeElapsed()).thenReturn(0L);
        when(getSettings().getCheckUpdateFrequencyMillis()).thenReturn(TimeUnit.HOURS.toMillis(6));

        final Schedule schedule = new Schedule(getSettings(), getTimeUtils());

        final long now = SystemClock.elapsedRealtime();
        assertThat(areTimesEqual(now, schedule.getNextCheckTime()), equalTo(true));
    }

    @Test
    public void getNextCheckTimeForOldCheck() {
        final long checkFrequency = 10;

        final long now = SystemClock.elapsedRealtime();

        when(getSettings().getLastCheckTimeElapsed()).thenReturn(now - checkFrequency * 2);
        when(getSettings().getCheckUpdateFrequencyMillis()).thenReturn(checkFrequency);

        final Schedule schedule = new Schedule(getSettings(), getTimeUtils());

        assertThat(areTimesEqual(now, schedule.getNextCheckTime()), equalTo(true));
    }

    @Test
    public void getNextCheckTimeForRecentCheck() {
        final long checkFrequency = 10;
        final long now = SystemClock.elapsedRealtime();

        when(getSettings().getLastCheckTimeElapsed()).thenReturn(now - checkFrequency / 3);
        when(getSettings().getCheckUpdateFrequencyMillis()).thenReturn(checkFrequency);

        final Schedule schedule = new Schedule(getSettings(), getTimeUtils());

        final long expectedCheckTime = now + checkFrequency * 2 / 3;
        final long actualCheckTime = schedule.getNextCheckTime();
        assertThat(areTimesEqual(expectedCheckTime, actualCheckTime), equalTo(true));
    }

    /**
     * Compares times ignoring milliseconds
     */
    private static boolean areTimesEqual(long time1, long time2) {
        final long millisPerSecond = 1000;
        final long time1NoMillis = time1 / millisPerSecond;
        final long time2NoMillis = time2 / millisPerSecond;
        return (time1NoMillis == time2NoMillis);
    }
}
