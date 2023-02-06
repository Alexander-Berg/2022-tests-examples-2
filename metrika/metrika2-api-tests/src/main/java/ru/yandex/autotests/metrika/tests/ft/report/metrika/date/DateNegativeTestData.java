package ru.yandex.autotests.metrika.tests.ft.report.metrika.date;

import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;

import javax.annotation.Nonnull;

import com.google.common.collect.Iterables;

import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.errors.AnalyticsReportError;
import ru.yandex.autotests.metrika.errors.ReportError;

import static com.google.common.collect.ImmutableList.of;
import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.utils.Utils.getDateAfterTomorrow;
import static ru.yandex.autotests.metrika.utils.Utils.getPlus7DaysDate;

public class DateNegativeTestData {
    @Nonnull
    public static Iterable<Object>[] getNegativeDateParameters() {
        return getNegativeDateParameters(ReportError.WRONG_START_OR_END_DATE, ReportError.WRONG_START_OR_END_DATE);
    }

    @Nonnull
    public static Iterable<Object>[] getNegativeDateGAParameters() {
        return getNegativeDateParameters(AnalyticsReportError.WRONG_START_OR_END_DATE, AnalyticsReportError.TYPE_CONVERSION_ERROR);
    }

    @Nonnull
    public static Collection<Object[]> toCollectionOfObjectArray(Iterable<Object>[] data) {
        return Arrays.stream(data)
                .map(i -> Iterables.toArray(i, Object.class))
                .collect(Collectors.toList());
    }

    @SuppressWarnings("unchecked")
    private static List<Object>[] getNegativeDateParameters(IExpectedError error, IExpectedError withNullError) {
        return new List[]{of("2015-02-02", "2015-02-01", error),
                asList("today", "yesterday", error),
                asList("yesterday", "2daysAgo", error),
                asList("2daysAgo", "3daysAgo", error),
                asList(null, "7daysAgo", withNullError),
                asList(getDateAfterTomorrow(), null, withNullError),

                asList("-2daysAgo", null, withNullError),
                asList("not-a-date", null, withNullError),
                asList("1999-12-31", getPlus7DaysDate(), error),
                asList("2000-01-01", getPlus7DaysDate() + 1, error)};
    }
}
