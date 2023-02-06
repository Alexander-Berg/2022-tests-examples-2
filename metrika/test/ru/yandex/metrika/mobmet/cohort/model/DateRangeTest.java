package ru.yandex.metrika.mobmet.cohort.model;

import java.time.LocalDate;
import java.time.ZoneId;
import java.time.ZonedDateTime;

import org.junit.Test;

import ru.yandex.metrika.mobmet.cohort.misc.CohortDates;
import ru.yandex.metrika.segments.core.query.paramertization.GroupType;

import static java.time.LocalTime.MIDNIGHT;
import static org.hamcrest.CoreMatchers.is;
import static org.hamcrest.MatcherAssert.assertThat;

public class DateRangeTest {
    private static final ZonedDateTime localTime =
            ZonedDateTime.of(LocalDate.of(2017, 3, 29), MIDNIGHT, ZoneId.of("Europe/Moscow"));

    @Test
    public void testDayIsClosed() throws Exception {
        DateRange dates = new CohortDates("2017-03-01", "2017-03-03", GroupType.day, localTime).enclosing("2017-03-26");
        assertThat("Day range is closed", dates.closed(), is(true));
    }

    @Test
    public void testWeekIsClosed() throws Exception {
        DateRange dates = new CohortDates("2017-03-01", "2017-03-03", GroupType.week, localTime).enclosing("2017-03-26");
        assertThat("Week range is closed", dates.closed(), is(true));
    }

    @Test
    public void testMonthIsClosed() throws Exception {
        DateRange dates = new CohortDates("2017-03-01", "2017-03-03", GroupType.month, localTime).enclosing("2017-02-28");
        assertThat("Month range is closed", dates.closed(), is(true));
    }

    @Test
    public void testDayIdOpen() throws Exception {
        DateRange dates = new CohortDates("2017-03-01", "2017-03-03", GroupType.day, localTime).enclosing("2017-03-29");
        assertThat("Day range is open", dates.closed(), is(false));
    }

    @Test
    public void testWeekIsOpen() throws Exception {
        DateRange dates = new CohortDates("2017-03-01", "2017-03-03", GroupType.week, localTime).enclosing("2017-03-27");
        assertThat("Week range is open", dates.closed(), is(false));
    }

    @Test
    public void testMonthIsOpen() throws Exception {
        DateRange dates = new CohortDates("2017-03-01", "2017-03-03", GroupType.month, localTime).enclosing("2017-03-01");
        assertThat("Month range is open", dates.closed(), is(false));
    }

    @Test
    public void testDayIsFuture() throws Exception {
        DateRange dates = new CohortDates("2017-03-01", "2017-03-03", GroupType.day, localTime).enclosing("2017-03-30");
        assertThat("Day range is future", dates.future(), is(true));
    }

    @Test
    public void testWeekIsFuture() throws Exception {
        DateRange dates = new CohortDates("2017-03-01", "2017-03-03", GroupType.week, localTime).enclosing("2017-04-03");
        assertThat("Week range is future", dates.future(), is(true));
    }

    @Test
    public void testMonthIsFuture() throws Exception {
        DateRange dates = new CohortDates("2017-03-01", "2017-03-03", GroupType.month, localTime).enclosing("2017-04-01");
        assertThat("Month range is future", dates.future(), is(true));
    }

    @Test
    public void testDayIsNotFuture() throws Exception {
        DateRange dates = new CohortDates("2017-03-01", "2017-03-03", GroupType.day, localTime).enclosing("2017-03-19");
        assertThat("Day range is future", dates.future(), is(false));
    }

    @Test
    public void testWeekIsNotFuture() throws Exception {
        DateRange dates = new CohortDates("2017-03-01", "2017-03-03", GroupType.week, localTime).enclosing("2017-04-02");
        assertThat("Week range is future", dates.future(), is(false));
    }

    @Test
    public void testMonthIsNotFuture() throws Exception {
        DateRange dates = new CohortDates("2017-03-01", "2017-03-03", GroupType.month, localTime).enclosing("2017-03-31");
        assertThat("Month range is future", dates.future(), is(false));
    }
}
