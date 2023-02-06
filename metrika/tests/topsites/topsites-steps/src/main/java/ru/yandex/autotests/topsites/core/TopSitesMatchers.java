package ru.yandex.autotests.topsites.core;

import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;

import org.hamcrest.BaseMatcher;
import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.joda.time.Days;

import ru.yandex.metrika.api.topsites.external.SiteRowExternal;
import ru.yandex.metrika.api.topsites.snapshot.ReportPeriod;

import static org.hamcrest.Matchers.equalTo;

public class TopSitesMatchers {

    public static Matcher<List<SiteRowExternal>> reportDataSortMatcher(List<SiteRowExternal> rows) {
        return equalTo(rows
                .stream()
                .sorted(Comparator.<SiteRowExternal, Long>comparing(r -> r.getCryptaMau().getValue()).reversed())
                .collect(Collectors.toList())
        );
    }

    public static Matcher<ReportPeriod> isPeriodOfWholeMonthOrWindowSize(int windowSize) {
        return new BaseMatcher<ReportPeriod>() {

            @Override
            public boolean matches(Object item) {
                ReportPeriod period = (ReportPeriod) item;
                return Days.daysBetween(period.getStart(), period.getEnd()).getDays() == windowSize
                        || (period.getStart().getDayOfMonth() == 1 && period.getEnd().plusDays(1).getDayOfMonth() == 1);
            }

            @Override
            public void describeTo(Description description) {
                description.appendText("ReportPeriod with days interval of " + windowSize + " days or whole month.");
            }
        };
    }
}
