package ru.yandex.metrika.mobmet.cohort.misc;

import java.time.LocalDate;
import java.util.List;

import org.junit.Test;

import ru.yandex.metrika.api.cohort.misc.CADateTimeHelper;
import ru.yandex.metrika.segments.core.query.paramertization.GroupType;
import ru.yandex.metrika.util.collections.F;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.contains;
import static ru.yandex.metrika.mobmet.cohort.misc.CohortDates.createDateGrid;

/**
 * Created by graev on 01/07/16.
 */
public class CADateTimeHelperTest {
    @Test
    public void createDateRangeForDays1() throws Exception {
        final List<LocalDate> result = createDateGrid("2016-06-01", "2016-06-03", GroupType.day);
        assertThat(F.map(result, CADateTimeHelper::dateAsString), contains("2016-06-01", "2016-06-02", "2016-06-03"));
    }

    @Test
    public void createDateRangeForDays2() throws Exception {
        final List<LocalDate> result = createDateGrid("2016-06-29", "2016-07-01", GroupType.day);
        assertThat(F.map(result, CADateTimeHelper::dateAsString), contains("2016-06-29", "2016-06-30", "2016-07-01"));
    }

    @Test
    public void createDateRangeForWeek() throws Exception {
        final List<LocalDate> result = createDateGrid("2016-06-01", "2016-06-15", GroupType.week);
        assertThat(F.map(result, CADateTimeHelper::dateAsString), contains("2016-06-01", "2016-06-06", "2016-06-13"));
    }

    @Test
    public void createDateRangeForMonth() throws Exception {
        final List<LocalDate> result = createDateGrid("2016-06-10", "2016-08-20", GroupType.month);
        assertThat(F.map(result, CADateTimeHelper::dateAsString), contains("2016-06-10", "2016-07-01", "2016-08-01"));
    }
}
