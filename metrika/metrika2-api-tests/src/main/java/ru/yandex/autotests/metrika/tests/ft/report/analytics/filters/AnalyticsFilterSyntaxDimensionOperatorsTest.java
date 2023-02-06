package ru.yandex.autotests.metrika.tests.ft.report.analytics.filters;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

/**
 * Created by sourx on 26.05.2016.
 */
@Features(Requirements.Feature.ANALYTICS)
@Stories({Requirements.Story.Report.Type.ANALYTICS, Requirements.Story.Report.Parameter.FILTERS})
@Title("Фильтры (google analytics): операторы для измерений")
@RunWith(Parameterized.class)
public class AnalyticsFilterSyntaxDimensionOperatorsTest extends AnalyticsFilterSyntaxBaseTest {
    private final static String METRIC = "ga:users";
    private final static String DIMENSION_PATH = "ga:pagePath";
    private final static String DIMENSION_INTEREST = "ga:interestAffinityCategory";
    private final static String DIMENSION_REFERRER = "ga:fullReferrer";
    private final static String DIMENSION_SESSION_DURATION = "ga:sessionDurationBucket";
    private final static String DIMENSION_SOURCE = "ga:source";

    @Parameterized.Parameters()
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {DIMENSION_PATH, METRIC, dimension(DIMENSION_PATH).equalTo("/search")},
                {DIMENSION_PATH, METRIC, dimension(DIMENSION_PATH).notEqualTo("/search")},
                {DIMENSION_PATH, METRIC, dimension(DIMENSION_PATH).greaterThan("/search")},
                {DIMENSION_PATH, METRIC, dimension(DIMENSION_PATH).lessThan("/search")},
                {DIMENSION_PATH, METRIC, dimension(DIMENSION_PATH).greaterThanOrEqualTo("/search")},
                {DIMENSION_PATH, METRIC, dimension(DIMENSION_PATH).lessThanOrEqualTo("/search")},
                {DIMENSION_PATH, METRIC, dimension(DIMENSION_PATH).matchRegEx("^search")},
                {DIMENSION_PATH, METRIC, dimension(DIMENSION_PATH).notMatchRegEx("^search")},
                {DIMENSION_PATH, METRIC, dimension(DIMENSION_PATH).matchSubstring("search")},
                {DIMENSION_PATH, METRIC, dimension(DIMENSION_PATH).notMatchSubstring("search")},

                {DIMENSION_INTEREST, METRIC, dimension(DIMENSION_INTEREST).equalTo("Cinema")},
                {DIMENSION_INTEREST, METRIC, dimension(DIMENSION_INTEREST).notEqualTo("Cinema")},

                {DIMENSION_REFERRER, METRIC, dimension(DIMENSION_REFERRER).notEqualTo("http://market.yandex.ru/")},
                {DIMENSION_REFERRER, METRIC, dimension(DIMENSION_REFERRER).notMatchSubstring("market")},
                {DIMENSION_REFERRER, METRIC, dimension(DIMENSION_REFERRER).notMatchRegEx(".*")},
                {DIMENSION_REFERRER, METRIC, dimension(DIMENSION_REFERRER).lessThan("http://market.yandex.ru/")},
                {DIMENSION_REFERRER, METRIC, dimension(DIMENSION_REFERRER).lessThanOrEqualTo("http://market.yandex.ru/")},
                {DIMENSION_REFERRER, METRIC, dimension(DIMENSION_REFERRER).equalTo("http://market.yandex.ru/")},
                {DIMENSION_REFERRER, METRIC, dimension(DIMENSION_REFERRER).matchSubstring("market")},
                {DIMENSION_REFERRER, METRIC, dimension(DIMENSION_REFERRER).matchRegEx(".*")},
                {DIMENSION_REFERRER, METRIC, dimension(DIMENSION_REFERRER).greaterThan("http://market.yandex.ru/")},
                {DIMENSION_REFERRER, METRIC, dimension(DIMENSION_REFERRER).greaterThanOrEqualTo("http://market.yandex.ru/")},

                {DIMENSION_SESSION_DURATION, METRIC, dimension(DIMENSION_SESSION_DURATION).notEqualTo(0)},
                {DIMENSION_SESSION_DURATION, METRIC, dimension(DIMENSION_SESSION_DURATION).lessThan(10)},
                {DIMENSION_SESSION_DURATION, METRIC, dimension(DIMENSION_SESSION_DURATION).lessThanOrEqualTo(10)},
                {DIMENSION_SESSION_DURATION, METRIC, dimension(DIMENSION_SESSION_DURATION).equalTo(0)},
                {DIMENSION_SESSION_DURATION, METRIC, dimension(DIMENSION_SESSION_DURATION).greaterThan(10)},
                {DIMENSION_SESSION_DURATION, METRIC, dimension(DIMENSION_SESSION_DURATION).greaterThanOrEqualTo(10)},
                {DIMENSION_SESSION_DURATION, METRIC, dimension(DIMENSION_SESSION_DURATION).notEqualTo("0")},
                {DIMENSION_SESSION_DURATION, METRIC, dimension(DIMENSION_SESSION_DURATION).lessThan("10")},
                {DIMENSION_SESSION_DURATION, METRIC, dimension(DIMENSION_SESSION_DURATION).lessThanOrEqualTo("10")},
                {DIMENSION_SESSION_DURATION, METRIC, dimension(DIMENSION_SESSION_DURATION).equalTo("0")},
                {DIMENSION_SESSION_DURATION, METRIC, dimension(DIMENSION_SESSION_DURATION).greaterThan("10")},
                {DIMENSION_SESSION_DURATION, METRIC, dimension(DIMENSION_SESSION_DURATION).greaterThanOrEqualTo("10")},

                {DIMENSION_SOURCE, METRIC, dimension(DIMENSION_SOURCE).equalTo("(direct)")},
                {DIMENSION_SOURCE, METRIC, dimension(DIMENSION_SOURCE).notEqualTo("(direct)")},
                {DIMENSION_SOURCE, METRIC, dimension(DIMENSION_SOURCE).greaterThan("(direct)")},
                {DIMENSION_SOURCE, METRIC, dimension(DIMENSION_SOURCE).greaterThanOrEqualTo("(direct)")},
                {DIMENSION_SOURCE, METRIC, dimension(DIMENSION_SOURCE).lessThan("(direct)")},
                {DIMENSION_SOURCE, METRIC, dimension(DIMENSION_SOURCE).greaterThanOrEqualTo("(direct)")},
                {DIMENSION_SOURCE, METRIC, dimension(DIMENSION_SOURCE).matchRegEx(".*")},
                {DIMENSION_SOURCE, METRIC, dimension(DIMENSION_SOURCE).notMatchRegEx(".*")},
                {DIMENSION_SOURCE, METRIC, dimension(DIMENSION_SOURCE).matchSubstring("direct")},
                {DIMENSION_SOURCE, METRIC, dimension(DIMENSION_SOURCE).notMatchSubstring("direct")},
        });
    }
}
