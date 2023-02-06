package com.yandex.launcher.updaterapp.utils;

import static junit.framework.Assert.assertEquals;
import static junit.framework.Assert.assertFalse;
import static junit.framework.Assert.assertTrue;

import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.when;

import androidx.annotation.NonNull;

import com.yandex.launcher.updaterapp.common.ApplicationConfig;
import com.yandex.launcher.updaterapp.common.utils.TimeUtils;
import com.yandex.launcher.updaterapp.BaseRobolectricTest;
import com.yandex.launcher.updaterapp.core.configure.Configuration;

import org.junit.Test;

import java.util.Calendar;
import java.util.GregorianCalendar;

public class TimeUtilsTest extends BaseRobolectricTest {

    @Test
    public void shouldDetectNightInstallPeriod() {
        final TimeUtils timeUtils = spy(new TimeUtils());
        final Configuration defaultConfiguration = new Configuration.Builder(ApplicationConfig.getInstance(getApp())).build();

        when(timeUtils.getNowCalendar()).thenReturn(getCalendar(2, 0));
        assertTrue(timeUtils.isNowNightInstallPeriod(defaultConfiguration.getNightIntervalStartTimeHours(),
                defaultConfiguration.getNightIntervalEndTimeHours()));

        when(timeUtils.getNowCalendar()).thenReturn(getCalendar(3, 0));
        assertTrue(timeUtils.isNowNightInstallPeriod(defaultConfiguration.getNightIntervalStartTimeHours(),
                defaultConfiguration.getNightIntervalEndTimeHours()));

        when(timeUtils.getNowCalendar()).thenReturn(getCalendar(6, 0));
        assertTrue(timeUtils.isNowNightInstallPeriod(defaultConfiguration.getNightIntervalStartTimeHours(),
                defaultConfiguration.getNightIntervalEndTimeHours()));

        when(timeUtils.getNowCalendar()).thenReturn(getCalendar(1, 59));
        assertFalse(timeUtils.isNowNightInstallPeriod(defaultConfiguration.getNightIntervalStartTimeHours(),
                defaultConfiguration.getNightIntervalEndTimeHours()));

        when(timeUtils.getNowCalendar()).thenReturn(getCalendar(6, 1));
        assertFalse(timeUtils.isNowNightInstallPeriod(defaultConfiguration.getNightIntervalStartTimeHours(),
                defaultConfiguration.getNightIntervalEndTimeHours()));

        when(timeUtils.getNowCalendar()).thenReturn(getCalendar(18, 0));
        assertFalse(timeUtils.isNowNightInstallPeriod(defaultConfiguration.getNightIntervalStartTimeHours(),
                defaultConfiguration.getNightIntervalEndTimeHours()));
    }

    @Test
    public void shouldReturnNightInstallTimeBeforeNightInstallPeriod() {
        final TimeUtils timeUtils = spy(new TimeUtils());
        final Configuration defaultConfiguration = new Configuration.Builder(ApplicationConfig.getInstance(getApp())).build();
        final int nightInstallHour = (defaultConfiguration.getNightIntervalStartTimeHours() + defaultConfiguration.getNightIntervalEndTimeHours()) / 2;

        when(timeUtils.getNowCalendar()).thenReturn(getCalendar(0, 0));
        assertEquals(getCalendar(nightInstallHour, 0).getTimeInMillis(),
                timeUtils.getNextNightInstallTime(defaultConfiguration.getNightIntervalStartTimeHours(), defaultConfiguration.getNightIntervalEndTimeHours()));

        when(timeUtils.getNowCalendar()).thenReturn(getCalendar(1, 23));
        assertEquals(getCalendar(nightInstallHour, 23).getTimeInMillis(),
                timeUtils.getNextNightInstallTime(defaultConfiguration.getNightIntervalStartTimeHours(), defaultConfiguration.getNightIntervalEndTimeHours()));
    }

    @Test
    public void shouldReturnNightInstallTimeAfterNightInstallPeriod() {
        final TimeUtils timeUtils = spy(new TimeUtils());
        final Configuration defaultConfiguration = new Configuration.Builder(ApplicationConfig.getInstance(getApp())).build();
        final int nightInstallHour = (defaultConfiguration.getNightIntervalStartTimeHours() + defaultConfiguration.getNightIntervalEndTimeHours()) / 2;

        when(timeUtils.getNowCalendar()).thenReturn(new GregorianCalendar(2016, 1, 1, 18, 1));
        assertEquals(
                new GregorianCalendar(2016, 1, 2, nightInstallHour, 1).getTimeInMillis(),
                timeUtils.getNextNightInstallTime(defaultConfiguration.getNightIntervalStartTimeHours(), defaultConfiguration.getNightIntervalEndTimeHours()));

        when(timeUtils.getNowCalendar()).thenReturn(new GregorianCalendar(2016, 0, 31, 23, 59));
        assertEquals(
                new GregorianCalendar(2016, 1, 1, nightInstallHour, 59).getTimeInMillis(),
                timeUtils.getNextNightInstallTime(defaultConfiguration.getNightIntervalStartTimeHours(), defaultConfiguration.getNightIntervalEndTimeHours()));
    }

    @Test
    public void shouldReturnNightInstallTimeWhileNightInstallPeriod() {
        final TimeUtils timeUtils = spy(new TimeUtils());
        final Configuration defaultConfiguration = new Configuration.Builder(ApplicationConfig.getInstance(getApp())).build();

        Calendar now = getCalendar(2, 0);

        when(timeUtils.getNowCalendar()).thenReturn(now);
        assertEquals(now.getTimeInMillis(), timeUtils.getNextNightInstallTime(defaultConfiguration.getNightIntervalStartTimeHours(),
                defaultConfiguration.getNightIntervalEndTimeHours()));

        now = getCalendar(4, 34);

        when(timeUtils.getNowCalendar()).thenReturn(now);
        assertEquals(now.getTimeInMillis(), timeUtils.getNextNightInstallTime(defaultConfiguration.getNightIntervalStartTimeHours(),
                defaultConfiguration.getNightIntervalEndTimeHours()));

        now = getCalendar(6, 0);

        when(timeUtils.getNowCalendar()).thenReturn(now);
        assertEquals(now.getTimeInMillis(), timeUtils.getNextNightInstallTime(defaultConfiguration.getNightIntervalStartTimeHours(),
                defaultConfiguration.getNightIntervalEndTimeHours()));
    }

    @NonNull
    private Calendar getCalendar(int hour, int minute) {
        return new GregorianCalendar(2016, 1, 1, hour, minute);
    }
}
