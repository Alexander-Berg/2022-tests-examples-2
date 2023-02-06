package ru.yandex.autotests.metrika.tests.ft.report.analytics.filters;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.errors.AnalyticsReportError;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

/**
 * Created by sourx on 27.05.2016.
 */
@Features(Requirements.Feature.ANALYTICS)
@Stories({Requirements.Story.Report.Type.ANALYTICS, Requirements.Story.Report.Parameter.FILTERS})
@Title("Фильтры (google analytics): операторы для измерений (негативные)")
@RunWith(Parameterized.class)
public class AnalyticsFilterSyntaxNegativeDimensionOperatorsTest extends AnalyticsFilterSyntaxNegativeBaseTest {
    private final static String METRIC = "ga:users";
    private final static String DIMENSION_INTEREST = "ga:interestAffinityCategory";
    private final static String DIMENSION_SESSION_DURATION = "ga:sessionDurationBucket";

    @Parameterized.Parameters()
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {DIMENSION_INTEREST, METRIC, dimension(DIMENSION_INTEREST).matchRegEx("^Cinema")},
                {DIMENSION_INTEREST, METRIC, dimension(DIMENSION_INTEREST).notMatchRegEx("^Cinema")},
                {DIMENSION_INTEREST, METRIC, dimension(DIMENSION_INTEREST).matchSubstring("Cinema")},
                {DIMENSION_INTEREST, METRIC, dimension(DIMENSION_INTEREST).notMatchSubstring("Cinema")},
                {DIMENSION_INTEREST, METRIC, dimension(DIMENSION_INTEREST).lessThan("Cinema")},
                {DIMENSION_INTEREST, METRIC, dimension(DIMENSION_INTEREST).lessThanOrEqualTo("Cinema")},
                {DIMENSION_INTEREST, METRIC, dimension(DIMENSION_INTEREST).greaterThan("Cinema")},
                {DIMENSION_INTEREST, METRIC, dimension(DIMENSION_INTEREST).greaterThanOrEqualTo("Cinema")},

                {DIMENSION_SESSION_DURATION, METRIC, dimension(DIMENSION_SESSION_DURATION).matchRegEx("^[0-9]+$")},
                {DIMENSION_SESSION_DURATION, METRIC, dimension(DIMENSION_SESSION_DURATION).notMatchRegEx("^[0-9]+$")},
                {DIMENSION_SESSION_DURATION, METRIC, dimension(DIMENSION_SESSION_DURATION).matchSubstring("1")},
                {DIMENSION_SESSION_DURATION, METRIC, dimension(DIMENSION_SESSION_DURATION).notMatchSubstring("1")},

        });
    }

    @Override
    protected IExpectedError getExpectedError() {
        return AnalyticsReportError.OPERATOR_NOT_SUPPORTES_FOR_DIMENSION;
    }
}
