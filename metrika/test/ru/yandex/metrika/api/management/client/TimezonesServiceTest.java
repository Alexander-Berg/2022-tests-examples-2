package ru.yandex.metrika.api.management.client;

import java.time.Instant;
import java.time.format.DateTimeFormatter;
import java.util.Collection;

import com.google.common.collect.ImmutableList;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import static org.junit.Assert.assertEquals;

/**
 * @author dancingelf
 */
@RunWith(Parameterized.class)
public class TimezonesServiceTest {

    private static final long SUMMER_TIMESTAMP =
            Instant.from(DateTimeFormatter.ISO_OFFSET_DATE_TIME.parse("2016-07-01T00:00:00+00:00")).toEpochMilli();
    private static final long WINTER_TIMESTAMP =
            Instant.from(DateTimeFormatter.ISO_OFFSET_DATE_TIME.parse("2016-01-01T00:00:00+00:00")).toEpochMilli();

    @Parameterized.Parameter
    public String timezone;

    @Parameterized.Parameter(1)
    public long timestamp;

    @Parameterized.Parameter(2)
    public String expected;

    @Test
    public void testTimezoneNames() {
        assertEquals(expected, TimezonesService.formatTzName(timezone, timestamp));
    }

    @Parameterized.Parameters
    public static Collection<Object[]> initParams() {
        return ImmutableList.<Object[]>builder()
                .add(params("Europe/Moscow", SUMMER_TIMESTAMP, "(UTC+03:00) Europe/Moscow"))
                .add(params("Europe/Moscow", WINTER_TIMESTAMP, "(UTC+03:00) Europe/Moscow"))
                .add(params("Europe/Samara", SUMMER_TIMESTAMP, "(UTC+04:00) Europe/Samara"))
                .add(params("Europe/Samara", WINTER_TIMESTAMP, "(UTC+04:00) Europe/Samara"))
                .add(params("UTC", SUMMER_TIMESTAMP, "UTC"))
                .add(params("Europe/London", SUMMER_TIMESTAMP, "(UTC+01:00) Europe/London"))
                .add(params("Europe/London", WINTER_TIMESTAMP, "(UTC) Europe/London"))
                .add(params("Asia/Kabul", SUMMER_TIMESTAMP, "(UTC+04:30) Asia/Kabul"))
                .add(params("Asia/Kabul", WINTER_TIMESTAMP, "(UTC+04:30) Asia/Kabul"))
                .add(params("America/New_York", SUMMER_TIMESTAMP, "(UTC-04:00) America/New_York"))
                .add(params("America/New_York", WINTER_TIMESTAMP, "(UTC-05:00) America/New_York"))
                .add(params("Pacific/Fiji", SUMMER_TIMESTAMP, "(UTC+12:00) Pacific/Fiji"))
                .add(params("Pacific/Fiji", WINTER_TIMESTAMP, "(UTC+13:00) Pacific/Fiji"))
                .build();
    }

    private static Object[] params(Object... params) {
        return params;
    }
}
