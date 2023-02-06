package ru.yandex.autotests.metrika.tests.ft.report.analytics.compatibility.filters;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.errors.AnalyticsReportError;
import ru.yandex.autotests.metrika.tests.ft.report.analytics.filters.AnalyticsFilterSyntaxNegativeBaseTest;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

/**
 * Created by sourx on 03.08.16.
 */
@Features(Requirements.Feature.ANALYTICS)
@Stories({Requirements.Story.Report.Type.ANALYTICS, Requirements.Story.Report.Parameter.FILTERS})
@Title("Фильтры (google analytics): операторы для измерений (совместимость, негативные)")
@RunWith(Parameterized.class)
public class AnalyticsCompatibilityFiltersDimensionNegativeTest extends AnalyticsFilterSyntaxNegativeBaseTest {
    private final static String DIMENSION_GOAL = "ym:s:goal";
    private final static String DIMENSION_VISIT_DURATION = "ym:s:visitDuration";

    private final static String METRIC_VISIT = "ym:s:visits";

    @Parameterized.Parameters()
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).greaterThan(1)},
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).lessThan(1)},
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).greaterThanOrEqualTo(1)},
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).lessThanOrEqualTo(1)},
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).matchSubstring("1")},
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).notMatchSubstring("1")},
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).matchRegEx(".*")},
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).notMatchRegEx(".*")},
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).matchStar("*")},
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).notMatchStar("*")},

                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).matchSubstring("1")},
                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).notMatchSubstring("1")},
                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).matchRegEx(".*")},
                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).notMatchRegEx(".*")},
                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).matchStar("*")},
                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).notMatchStar("*")},
        });
    }

    @Override
    protected IExpectedError getExpectedError() {
        return AnalyticsReportError.OPERATOR_NOT_SUPPORTES_FOR_DIMENSION;
    }
}
