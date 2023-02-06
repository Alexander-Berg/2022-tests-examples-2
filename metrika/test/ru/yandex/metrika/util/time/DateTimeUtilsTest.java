package ru.yandex.metrika.util.time;

import java.time.LocalDate;
import java.time.LocalTime;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.util.Collection;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.stream.Stream;

import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import static java.util.List.of;
import static ru.yandex.metrika.util.time.DateTimeUtils.getMillisBeforeClosestPeriod;

@RunWith(Parameterized.class)
public class DateTimeUtilsTest {
    @Parameterized.Parameter
    public LocalTime periodStartTime;

    @Parameterized.Parameter(1)
    public LocalTime periodEndTime;

    @Parameterized.Parameter(2)
    public ZonedDateTime fromTime;

    @Parameterized.Parameter(3)
    public long expectedMillis;

    @Parameterized.Parameters
    public static Collection<Object[]> createParams() {
        return Stream.of(
                of(
                        LocalTime.of(9, 0),
                        LocalTime.of(20, 0),
                        ZonedDateTime.of(LocalDate.now(), LocalTime.of(8, 0), ZoneId.of("ACT", ZoneId.SHORT_IDS)),
                        TimeUnit.HOURS.toMillis(1)
                ),
                of(
                        LocalTime.of(9, 0),
                        LocalTime.of(20, 0),
                        ZonedDateTime.of(LocalDate.now(), LocalTime.of(10, 0), ZoneId.of("ACT", ZoneId.SHORT_IDS)),
                        TimeUnit.HOURS.toMillis(0)
                ),
                of(
                        LocalTime.of(9, 0),
                        LocalTime.of(20, 0),
                        ZonedDateTime.of(LocalDate.now(), LocalTime.of(22, 0), ZoneId.of("ACT", ZoneId.SHORT_IDS)),
                        TimeUnit.HOURS.toMillis(11)
                ),
                of(
                        LocalTime.of(9, 0),
                        LocalTime.of(20, 0),
                        ZonedDateTime.of(LocalDate.now(), LocalTime.of(20, 0), ZoneId.of("ACT", ZoneId.SHORT_IDS)),
                        TimeUnit.HOURS.toMillis(0)
                ),
                of(
                        LocalTime.of(9, 0),
                        LocalTime.of(20, 0),
                        ZonedDateTime.of(LocalDate.now(), LocalTime.of(9, 0), ZoneId.of("ACT", ZoneId.SHORT_IDS)),
                        TimeUnit.HOURS.toMillis(0)
                )
        ).map(List::toArray).toList();
    }

    @Test
    public void test() {
        Assert.assertEquals(expectedMillis, getMillisBeforeClosestPeriod(periodStartTime, periodEndTime, fromTime));
    }

    @Test(expected = IllegalArgumentException.class)
    public void testNegative() {
        getMillisBeforeClosestPeriod(LocalTime.of(15, 0), LocalTime.of(9, 0), ZonedDateTime.of(LocalDate.now(), LocalTime.of(9, 0), ZoneId.of("ACT", ZoneId.SHORT_IDS)));
    }
}
