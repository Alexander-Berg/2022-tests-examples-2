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
import static ru.yandex.autotests.metrika.filters.Term.metric;

/**
 * Created by sourx on 03.08.16.
 */
@Features(Requirements.Feature.ANALYTICS)
@Stories({Requirements.Story.Report.Type.ANALYTICS, Requirements.Story.Report.Parameter.FILTERS})
@Title("Фильтры (google analytics): операторы для метрик (совместимость, негативные)")
@RunWith(Parameterized.class)
public class AnalyticsCompatibilityFiltersMetricNegativeTest extends AnalyticsFilterSyntaxNegativeBaseTest {
    private final static String DIMENSION = "ym:s:goal";
    private final static String METRIC = "ym:s:users";
    private final static String METRIC_IN_SET = "ym:s:paramsNumber";

    @Parameterized.Parameters()
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {DIMENSION, METRIC, metric(METRIC).matchSubstring("1")},
                {DIMENSION, METRIC, metric(METRIC).notMatchSubstring("1")},
                {DIMENSION, METRIC, metric(METRIC).matchRegEx(".*")},
                {DIMENSION, METRIC, metric(METRIC).notMatchRegEx(".*")},
                {DIMENSION, METRIC, metric(METRIC).matchStar("*")},
                {DIMENSION, METRIC, metric(METRIC).notMatchStar("*")},

                {DIMENSION, METRIC_IN_SET, metric(METRIC_IN_SET).matchSubstring("1")},
                {DIMENSION, METRIC_IN_SET, metric(METRIC_IN_SET).notMatchSubstring("1")},
                {DIMENSION, METRIC_IN_SET, metric(METRIC_IN_SET).matchRegEx(".*")},
                {DIMENSION, METRIC_IN_SET, metric(METRIC_IN_SET).notMatchRegEx(".*")},
                {DIMENSION, METRIC_IN_SET, metric(METRIC_IN_SET).matchStar("*")},
                {DIMENSION, METRIC_IN_SET, metric(METRIC_IN_SET).notMatchStar("*")},
        });
    }

    @Override
    protected IExpectedError getExpectedError() {
        return AnalyticsReportError.OPERATOR_NOT_SUPPORTED_FOR_METRIC;
    }
}
