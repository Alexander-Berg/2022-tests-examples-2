package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table.syntax;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.errors.ReportError;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.filters.MetricExpression.metricFilter;
import static ru.yandex.autotests.metrika.filters.Term.metric;

/**
 * Created by konkov on 08.05.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.FILTERS})
@Title("Фильтры: фильтрация метрики по измерениям множества (негативные)")
@RunWith(Parameterized.class)
public class FilterSyntaxNegativeMetricBySetTest extends FilterNegativeBaseTest {

    private final static String DIMENSION = "ym:s:goal";
    private final static String METRIC = "ym:s:visits";

    @Parameterized.Parameters(name = "{1}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {DIMENSION, metricFilter(METRIC, metric("ym:s:users").greaterThan(1)), null},
        });
    }

    @Override
    protected IExpectedError getExpectedError() {
        return ReportError.WRONG_METRIC;
    }
}
