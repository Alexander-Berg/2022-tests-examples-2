package ru.yandex.metrika.api.cohort.misc;

import java.time.LocalDate;
import java.util.List;

import org.junit.Test;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.metrika.api.cohort.misc.CADateTimeHelper.parseDate;
import static ru.yandex.metrika.api.cohort.misc.CAUtils.generateDateCohortIds;
import static ru.yandex.metrika.api.cohort.model.CAGroupMethod.calendar;
import static ru.yandex.metrika.api.cohort.model.CAGroupMethod.window;
import static ru.yandex.metrika.segments.core.query.paramertization.GroupType.day;
import static ru.yandex.metrika.segments.core.query.paramertization.GroupType.month;
import static ru.yandex.metrika.segments.core.query.paramertization.GroupType.week;

public class CAGeneratedDatesTest {

    @Test
    public void generateForDays() {
        LocalDate date1 = parseDate("2016-06-01");
        LocalDate date2 = parseDate("2016-06-07");
        List<String> result = generateDateCohortIds(
                day, date1, date2,
                parseDate("2021-01-01"), day, window, 2, 3);
        assertThat(result, equalTo(List.of("2016-06-04", "2016-06-05")));
    }

    @Test
    public void generateForWeeks() {
        LocalDate date1 = parseDate("2016-06-10");
        LocalDate date2 = parseDate("2016-06-23");
        List<String> result = generateDateCohortIds(
                week, date1, date2,
                parseDate("2021-01-01"), day, window, 10, 0);
        assertThat(result, equalTo(List.of("2016-06-06", "2016-06-13", "2016-06-20")));
    }

    @Test
    public void generateForMonths() {
        LocalDate date1 = parseDate("2016-06-01");
        LocalDate date2 = parseDate("2016-08-20");
        List<String> result = generateDateCohortIds(
                month, date1, date2,
                parseDate("2021-01-01"), day, window, 10, 0);
        assertThat(result, equalTo(List.of("2016-06-01", "2016-07-01", "2016-08-01")));
    }

    @Test
    public void generateDaysUntilToday() {
        LocalDate date1 = parseDate("2016-06-01");
        LocalDate date2 = parseDate("2016-06-07");
        LocalDate appToday = parseDate("2016-06-03");
        List<String> result = generateDateCohortIds(
                day, date1, date2,
                appToday, day, calendar, 10, 0);
        assertThat(result, equalTo(List.of("2016-06-01", "2016-06-02", "2016-06-03")));
    }

    @Test
    public void generateWeeksUntilToday() {
        LocalDate date1 = parseDate("2016-06-10");
        LocalDate date2 = parseDate("2016-06-23");
        LocalDate appToday = parseDate("2016-07-25");
        List<String> result = generateDateCohortIds(
                week, date1, date2,
                appToday, week, calendar, 10, 0);
        assertThat(result, equalTo(List.of("2016-06-06", "2016-06-13", "2016-06-20")));
    }

    @Test
    public void generateMonthsUntilToday() {
        LocalDate date1 = parseDate("2016-06-01");
        LocalDate date2 = parseDate("2016-10-20");
        LocalDate appToday = parseDate("2016-08-15");
        List<String> result = generateDateCohortIds(
                month, date1, date2,
                appToday, month, calendar, 10, 0);
        assertThat(result, equalTo(List.of("2016-06-01", "2016-07-01", "2016-08-01")));
    }

    @Test
    public void generateIncompleteWeek() {
        LocalDate date1 = parseDate("2016-06-10");
        LocalDate date2 = parseDate("2016-06-23");
        LocalDate appToday = parseDate("2016-06-25");
        List<String> result = generateDateCohortIds(
                week, date1, date2,
                appToday, day, calendar, 10, 0);
        // Это случай, когда когорты - недели, а периоды - дни.
        // При этом в неделе "2020-06-20" календарные периоды-дни есть, но их просто меньше 7.
        assertThat(result, equalTo(List.of("2016-06-06", "2016-06-13", "2016-06-20")));
    }

    @Test
    public void generateMonthsUntilTodayWindow() {
        LocalDate date1 = parseDate("2016-06-01");
        LocalDate date2 = parseDate("2016-10-20");
        LocalDate appToday = parseDate("2016-09-15");
        List<String> result = generateDateCohortIds(
                month, date1, date2,
                appToday, month, window, 10, 0);
        assertThat(result, equalTo(List.of("2016-06-01", "2016-07-01", "2016-08-01", "2016-09-01")));
    }
}
