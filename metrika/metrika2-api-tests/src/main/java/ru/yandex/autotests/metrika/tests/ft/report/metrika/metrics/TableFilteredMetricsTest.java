package ru.yandex.autotests.metrika.tests.ft.report.metrika.metrics;

import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.function.Predicate;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.commons.rules.ParametersIgnoreRule;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.filters.Expression;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.anything;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.EXPENSES_VISITS;
import static ru.yandex.autotests.metrika.filters.MetricExpression.metricFilter;
import static ru.yandex.autotests.metrika.filters.MetricExpression.metricFilter2;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.any;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.cdp;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.table;
import static ru.yandex.autotests.metrika.utils.AllureUtils.addTestParameter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.Lists2.transpose;

/**
 * Created by konkov on 20.08.2014.
 */
@Features({Requirements.Feature.REPORT})
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.METRICS})
@Title("Отчет 'таблица': метрики с фильтром")
@RunWith(Parameterized.class)
public class TableFilteredMetricsTest extends TableMetricsTest {

    @Rule
    public ParametersIgnoreRule ignoreRule = new ParametersIgnoreRule();

    /**
     * фильтр на котором проверяются все метрики.
     */
    private static final Map<Predicate<String>, Expression> FILTERS = ImmutableMap.of(
            table(EXPENSES_VISITS), dimension("ym:ev:LastUTMMedium").equalTo("search"),
            cdp(), dimension("ym:s:gender").equalTo("female"),
            any(), dimension("ym:s:gender").equalTo("male")
    );

    @Before
    public void setup() {
        Expression filter = FILTERS.entrySet().stream()
                .filter(e -> e.getKey().test(metricName))
                .map(Map.Entry::getValue)
                .findFirst()
                .orElseThrow(IllegalStateException::new);

        ImmutableList<String> metrics = ImmutableList.of(metricFilter(metricName, filter), metricFilter2(metricName, filter));
        addTestParameter("Метрики", metrics.toString());
        addTestParameter("Остальное", tail.toString());
        result = user.onReportSteps().getTableReportAndExpectSuccess(
                tail,
                new CommonReportParameters().withMetrics(metrics));
    }

    @Test
    @IgnoreParameters(reason = "METR-23460", tag = "pvl")
    @IgnoreParameters(reason = "METR-31915", tag = "adfox")
    public void checkMetricValues() {
        // в запросе две метрики, поэтому metrics - это список из списков длиной два
        // после транспонирования получается два списка, которые должны быть равны.
        List<List<Double>> metrics = user.onResultSteps().getMetrics(result);
        List<List<Double>> transposed = transpose(metrics);

        assertThat("метрики с разными скобками равны", transposed.get(0), equalTo(transposed.get(1)));
    }


    @IgnoreParameters.Tag(name = "pvl")
    public static Collection<Object[]> ignoreParameters() {
        return asList(new Object[][]{
                {equalTo("ym:s:pvl<offline_region>Region<offline_window>Window"), anything()},
                {equalTo("ym:s:pvl<offline_point>Point<offline_window>Window"), anything()}
        });
    }

    @IgnoreParameters.Tag(name = "adfox")
    public static Collection<Object[]> ignoreParametersAdfox() {
        return asList(new Object[][]{
                {containsString("adfox"), anything()}
        });
    }
}
