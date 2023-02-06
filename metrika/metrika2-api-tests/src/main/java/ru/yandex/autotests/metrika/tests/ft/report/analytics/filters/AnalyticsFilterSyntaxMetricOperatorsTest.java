package ru.yandex.autotests.metrika.tests.ft.report.analytics.filters;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
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
@Title("Фильтры (google analytics): операторы для метрик")
@RunWith(Parameterized.class)
public class AnalyticsFilterSyntaxMetricOperatorsTest extends AnalyticsFilterSyntaxBaseTest {
    private final static String DIMENSION = "ga:country";
    private final static String METRIC = "ga:users";

    @Parameterized.Parameters()
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {DIMENSION, METRIC, metric(METRIC).equalTo(0)},
                {DIMENSION, METRIC, metric(METRIC).greaterThan(0)},
                {DIMENSION, METRIC, metric(METRIC).lessThan(0)},
                {DIMENSION, METRIC, metric(METRIC).greaterThanOrEqualTo(0)},
                {DIMENSION, METRIC, metric(METRIC).lessThanOrEqualTo(0)},
                {DIMENSION, METRIC, metric(METRIC).notEqualTo(0)}
        });
    }
}
