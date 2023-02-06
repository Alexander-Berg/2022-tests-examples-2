package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table.syntax;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.filters.MetricExpression.metricFilter;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

/**
 * Created by konkov on 08.05.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.FILTERS})
@Title("Фильтры: фильтрация метрики по измерениям множества")
@RunWith(Parameterized.class)
public class FilterSyntaxMetricBySetTest extends FilterSyntaxBaseTest {

    private final static String DIMENSION = "ym:s:goal";
    private final static String METRIC = "ym:s:visits";

    @Parameterized.Parameters(name = "{1}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {DIMENSION, metricFilter(METRIC, dimension("ym:s:paramsLevel1").equalTo(null)), null},
                {DIMENSION, metricFilter(METRIC, dimension("ym:s:paramsLevel1").equalTo("a")), null},
                {DIMENSION, metricFilter(METRIC, dimension("ym:s:paramsLevel1").notEqualTo("a")), null},
                {DIMENSION, metricFilter(METRIC, dimension("ym:s:paramsLevel1").in("a")), null},
                {DIMENSION, metricFilter(METRIC, dimension("ym:s:paramsLevel1").in("a", "b")), null},
                {DIMENSION, metricFilter(METRIC, dimension("ym:s:paramsLevel1").notIn("a", "b")), null},
                {DIMENSION, metricFilter(METRIC, dimension("ym:s:pageViews").greaterThan(1)), null},
                {DIMENSION, metricFilter(METRIC, dimension("ym:s:interest").equalTo("literature")), null},
                {DIMENSION, metricFilter(METRIC, dimension("ym:s:interest").in("literature")), null},
                {DIMENSION, metricFilter(METRIC, dimension("ym:s:interest").in("literature", "cinema")), null},
                {DIMENSION, metricFilter(METRIC, dimension("ym:s:interest").notIn("literature", "cinema")), null},
        });
    }
}
