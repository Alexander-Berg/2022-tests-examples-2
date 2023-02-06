package ru.yandex.metrika.publishers.processor.parser;

import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.util.List;

import org.junit.Assert;
import org.junit.BeforeClass;
import org.junit.Test;
import org.mockito.Mockito;

import ru.yandex.metrika.counters.serverstate.CountersServerTimeZoneState;
import ru.yandex.metrika.managers.DbTimeZone;
import ru.yandex.metrika.managers.TimeZones;

public class PublishersDateParserTest {

    private static final int COUNTER_ID = 42;

    private static PublishersDateParser publishersDateParser;

    @BeforeClass
    public static void init() {
        CountersServerTimeZoneState timeZoneState = Mockito.mock(CountersServerTimeZoneState.class);
        Mockito.when(timeZoneState.getTimeZoneId(COUNTER_ID)).thenReturn(COUNTER_ID);

        DbTimeZone dbTz = new DbTimeZone();
        dbTz.setName("UTC");
        TimeZones timeZones = Mockito.mock(TimeZones.class);
        Mockito.when(timeZones.getTimeZoneById(COUNTER_ID)).thenReturn(dbTz);

        publishersDateParser = new PublishersDateParserMulti(List.of(
                new PublishersDateParserISO8601(timeZoneState, timeZones),
                new PublishersDateParserRFC822(timeZoneState, timeZones)
        ));
    }

    @Test
    public void testISO8601() {
        Long expected = ZonedDateTime.of(2018, 12, 11, 4, 30, 0, 0, ZoneOffset.UTC)
                .toInstant().toEpochMilli();

        Assert.assertEquals(expected, publishersDateParser.parse(COUNTER_ID, "2018-12-11T07:30:00.000+03:00").get());
        Assert.assertEquals(expected, publishersDateParser.parse(COUNTER_ID, "2018-12-11T07:30:00+03:00").get());
        Assert.assertEquals(expected, publishersDateParser.parse(COUNTER_ID, "2018-12-11T07:30:00.000+03").get());
        Assert.assertEquals(expected, publishersDateParser.parse(COUNTER_ID, "2018-12-11T07:30:00+03").get());
        Assert.assertEquals(expected, publishersDateParser.parse(COUNTER_ID, "2018-12-11T07:30:00.000+0300").get());
        Assert.assertEquals(expected, publishersDateParser.parse(COUNTER_ID, "2018-12-11T07:30:00+0300").get());
        Assert.assertEquals(expected, publishersDateParser.parse(COUNTER_ID, "2018-12-11T04:30:00.000Z").get());
        Assert.assertEquals(expected, publishersDateParser.parse(COUNTER_ID, "2018-12-11T04:30:00Z").get());
    }
}
