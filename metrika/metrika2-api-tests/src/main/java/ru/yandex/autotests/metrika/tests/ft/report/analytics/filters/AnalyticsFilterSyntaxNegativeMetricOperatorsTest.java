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
import static ru.yandex.autotests.metrika.filters.Term.metric;

/**
 * Created by sourx on 27.05.2016.
 */
@Features(Requirements.Feature.ANALYTICS)
@Stories({Requirements.Story.Report.Type.ANALYTICS, Requirements.Story.Report.Parameter.FILTERS})
@Title("Фильтры (google analytics): операторы для метрик (негативные)")
@RunWith(Parameterized.class)
public class AnalyticsFilterSyntaxNegativeMetricOperatorsTest extends AnalyticsFilterSyntaxNegativeBaseTest {
    private final static String DIMENSION = "ga:country";
    private final static String METRIC = "ga:users";

    @Parameterized.Parameters()
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {DIMENSION, METRIC, metric(METRIC).matchSubstring("1")},
                {DIMENSION, METRIC, metric(METRIC).notMatchSubstring("1")},
                {DIMENSION, METRIC, metric(METRIC).matchRegEx("^[0-9]+$")},
                {DIMENSION, METRIC, metric(METRIC).notMatchRegEx("^[0-9]+$")},
        });
    }

    @Override
    protected IExpectedError getExpectedError() {
        return AnalyticsReportError.OPERATOR_NOT_SUPPORTED_FOR_METRIC;
    }
}
