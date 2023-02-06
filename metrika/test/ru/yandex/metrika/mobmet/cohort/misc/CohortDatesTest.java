package ru.yandex.metrika.mobmet.cohort.misc;

import java.time.LocalDate;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.util.List;

import com.google.common.collect.ImmutableList;
import org.junit.Test;

import ru.yandex.metrika.mobmet.cohort.model.DateRange;
import ru.yandex.metrika.segments.core.query.paramertization.GroupType;

import static java.time.LocalTime.MIDNIGHT;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.is;
import static org.hamcrest.MatcherAssert.assertThat;

/**
 * Created by graev on 27/03/2017.
 */
public class CohortDatesTest {

    private static final ZonedDateTime localTime =
            ZonedDateTime.of(LocalDate.of(2017, 3, 29), MIDNIGHT, ZoneId.of("Europe/Moscow"));

    @Test
    public void testPlusDay() throws Exception {
        final CohortDates dates = new CohortDates("2017-03-01", "2017-03-03", GroupType.day, localTime);
        assertThat("Day range 'plus' operation is correct", dates.enclosing("2017-03-01").plus(2),
                equalTo(dates.enclosing("2017-03-03")));
    }

    @Test
    public void testPlusWeek() throws Exception {
        final CohortDates dates = new CohortDates("2017-03-01", "2017-03-03", GroupType.week, localTime);
        assertThat("Week range 'plus' operation is correct", dates.enclosing("2017-03-01").plus(2),
                equalTo(dates.enclosing("2017-03-13")));
    }

    @Test
    public void testPlusMonth() throws Exception {
        final CohortDates dates = new CohortDates("2017-03-01", "2017-03-03", GroupType.month, localTime);
        assertThat("Month range 'plus' operation is correct", dates.enclosing("2017-03-01").plus(2),
                equalTo(dates.enclosing("2017-05-01")));
    }

    @Test
    public void testCurrent() throws Exception {
        final CohortDates dates = new CohortDates("2017-03-01", "2017-03-03", GroupType.day, localTime);
        assertThat("Current date is returned correctly", dates.appLocalDate(), equalTo(localTime.toLocalDate()));

    }

    @Test
    public void testEnclosingDay() throws Exception {
        final CohortDates dates = new CohortDates("2017-03-01", "2017-03-03", GroupType.day, localTime);
        final DateRange range = dates.enclosing("2017-03-10");

        assertThat("Day enclosing works OK", range.from(), is(LocalDate.of(2017, 3, 10)));
        assertThat("Day enclosing works OK", range.to(), is(LocalDate.of(2017, 3, 10)));
    }

    @Test
    public void testEnclosingWeek() throws Exception {
        final CohortDates dates = new CohortDates("2017-03-01", "2017-03-03", GroupType.week, localTime);
        final DateRange range = dates.enclosing("2017-03-10");

        assertThat("Week enclosing works OK", range.from(), is(LocalDate.of(2017, 3, 6)));
        assertThat("Week enclosing works OK", range.to(), is(LocalDate.of(2017, 3, 12)));
    }

    @Test
    public void testEnclosingMonth() throws Exception {
        final CohortDates dates = new CohortDates("2017-03-01", "2017-03-03", GroupType.month, localTime);
        final DateRange range = dates.enclosing("2017-03-10");

        assertThat("Month enclosing works OK", range.from(), is(LocalDate.of(2017, 3, 1)));
        assertThat("Month enclosing works OK", range.to(), is(LocalDate.of(2017, 3, 31)));
    }

    @Test
    public void testDayCohorts() throws Exception {
        final CohortDates dates = new CohortDates("2017-03-01", "2017-03-03", GroupType.day, localTime);
        assertThat("Day cohorts are OK", dates.cohorts(),
                equalTo(ImmutableList.of(
                        dates.enclosing("2017-03-01"),
                        dates.enclosing("2017-03-02"),
                        dates.enclosing("2017-03-03")
                )));
    }

    @Test
    public void testWeekCohorts() throws Exception {
        final CohortDates dates = new CohortDates("2017-03-01", "2017-03-10", GroupType.week, localTime);
        final List<DateRange> cohorts = dates.cohorts();

        assertThat("Week cohorts are OK", cohorts.size(), is(2));
        assertThat("Week cohorts are OK", cohorts.get(0).from(), is(LocalDate.of(2017, 3, 1)));
        assertThat("Week cohorts are OK", cohorts.get(0).to(), is(LocalDate.of(2017, 3, 5)));
        assertThat("Week cohorts are OK", cohorts.get(1).from(), is(LocalDate.of(2017, 3, 6)));
        assertThat("Week cohorts are OK", cohorts.get(1).to(), is(LocalDate.of(2017, 3, 10)));
    }

    @Test
    public void testMonthCohorts() throws Exception {
        final CohortDates dates = new CohortDates("2017-03-10", "2017-04-11", GroupType.month, localTime);
        final List<DateRange> cohorts = dates.cohorts();

        assertThat("Month cohorts are OK", cohorts.size(), is(2));
        assertThat("Month cohorts are OK", cohorts.get(0).from(), is(LocalDate.of(2017, 3, 10)));
        assertThat("Month cohorts are OK", cohorts.get(0).to(), is(LocalDate.of(2017, 3, 31)));
        assertThat("Month cohorts are OK", cohorts.get(1).from(), is(LocalDate.of(2017, 4, 1)));
        assertThat("Month cohorts are OK", cohorts.get(1).to(), is(LocalDate.of(2017, 4, 11)));
    }

}
