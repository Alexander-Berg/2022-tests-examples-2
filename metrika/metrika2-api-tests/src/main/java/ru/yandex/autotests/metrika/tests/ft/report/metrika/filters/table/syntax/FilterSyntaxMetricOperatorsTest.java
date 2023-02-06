package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table.syntax;

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
 * Created by konkov on 08.05.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.FILTERS})
@Title("Фильтры: операторы для метрик")
@RunWith(Parameterized.class)
public class FilterSyntaxMetricOperatorsTest extends FilterSyntaxBaseTest {
    private final static String DIMENSION = "ym:s:goal";
    private final static String METRIC = "ym:s:users";
    private final static String METRIC_IN_SET = "ym:s:paramsNumber";

    @Parameterized.Parameters()
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {DIMENSION, METRIC, metric(METRIC).equalTo(0)},
                {DIMENSION, METRIC, metric(METRIC).greaterThan(0)},
                {DIMENSION, METRIC, metric(METRIC).lessThan(0)},
                {DIMENSION, METRIC, metric(METRIC).greaterThanOrEqualTo(0)},
                {DIMENSION, METRIC, metric(METRIC).lessThanOrEqualTo(0)},
                {DIMENSION, METRIC, metric(METRIC).notEqualTo(0)},

                {DIMENSION, METRIC_IN_SET, metric(METRIC_IN_SET).equalTo(0)},
                {DIMENSION, METRIC_IN_SET, metric(METRIC_IN_SET).greaterThan(0)},
                {DIMENSION, METRIC_IN_SET, metric(METRIC_IN_SET).lessThan(0)},
                {DIMENSION, METRIC_IN_SET, metric(METRIC_IN_SET).greaterThanOrEqualTo(0)},
                {DIMENSION, METRIC_IN_SET, metric(METRIC_IN_SET).lessThanOrEqualTo(0)},
                {DIMENSION, METRIC_IN_SET, metric(METRIC_IN_SET).notEqualTo(0)},
        });
    }
}
