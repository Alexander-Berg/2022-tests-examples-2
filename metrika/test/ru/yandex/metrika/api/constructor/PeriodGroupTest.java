package ru.yandex.metrika.api.constructor;

import org.junit.Test;

import ru.yandex.metrika.segments.core.query.paramertization.GroupType;

import static org.hamcrest.Matchers.contains;
import static org.junit.Assert.assertThat;

/**
 * Created by graev on 07/07/16.
 */
public class PeriodGroupTest {
    @Test
    public void testGridByDay() {
        final PeriodGroup dayPG = new PeriodGroup(GroupType.day, "2016-04-01", "2016-04-03");
        assertThat(dayPG.asList(), contains(
                contains("2016-04-01", "2016-04-01"),
                contains("2016-04-02", "2016-04-02"),
                contains("2016-04-03", "2016-04-03")));
    }

    @Test
    public void testGridByWeek() {
        final PeriodGroup weekPG = new PeriodGroup(GroupType.week, "2016-04-01", "2016-04-07");
        assertThat(weekPG.asList(), contains(
                contains("2016-04-01", "2016-04-03"),
                contains("2016-04-04", "2016-04-07")));
    }

    @Test
    public void testGridByMonth() {
        final PeriodGroup monthPG = new PeriodGroup(GroupType.month, "2016-04-10", "2016-06-20");
        assertThat(monthPG.asList(), contains(
                contains("2016-04-10", "2016-04-30"),
                contains("2016-05-01", "2016-05-31"),
                contains("2016-06-01", "2016-06-20")));
    }
}
