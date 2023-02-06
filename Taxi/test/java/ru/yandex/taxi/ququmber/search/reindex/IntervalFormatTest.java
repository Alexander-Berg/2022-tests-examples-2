package ru.yandex.taxi.ququmber.search.reindex;

import org.joda.time.DateTime;
import org.joda.time.Duration;
import org.joda.time.Interval;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class IntervalFormatTest {

    @Test
    public void test() {
        DateTime now = new DateTime();
        Interval interval = new Interval(now.minusDays(121).minusMinutes(90), now);
        Duration duration = interval.toDuration();
        Assertions.assertEquals("121d 1h 30m", IntervalFormat.format(duration));
    }
}
