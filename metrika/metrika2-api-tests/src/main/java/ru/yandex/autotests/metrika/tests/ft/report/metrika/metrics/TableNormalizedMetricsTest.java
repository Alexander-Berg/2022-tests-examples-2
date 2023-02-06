package ru.yandex.autotests.metrika.tests.ft.report.metrika.metrics;

import java.util.Collection;
import java.util.List;

import com.google.common.collect.ImmutableList;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.anything;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.filters.MetricExpression.metricFunction;
import static ru.yandex.autotests.metrika.matchers.NormalizedMatchers.isNormalized;
import static ru.yandex.autotests.metrika.utils.AllureUtils.addTestParameter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.Lists2.transpose;

/**
 * Created by konkov on 20.08.2014.
 */
@Features({Requirements.Feature.REPORT})
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.METRICS})
@Title("Отчет 'таблица': метрики в процентах")
@RunWith(Parameterized.class)
public class TableNormalizedMetricsTest extends TableMetricsTest {

    @Before
    public void setup() {
        ImmutableList<String> metrics = ImmutableList.of(metricName, metricFunction("norm", metricName));
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
        // после транспонирования получается два списка, в одном из которых сумма 100%
        List<List<Double>> metrics = user.onResultSteps().getMetrics(result);
        List<List<Double>> transposed = transpose(metrics);

        List<Double> rawMetric = transposed.get(0);
        List<Double> normalizedMetric = transposed.get(1);

        List<Double> rawTotals = result.getTotals();

        assertThat("метрика отнормирована корректно", normalizedMetric, isNormalized(rawMetric, rawTotals.get(0)));
    }

    @IgnoreParameters.Tag(name = "pvl")
    public static Collection<Object[]> ignoreParameters() {
        return asList(new Object[][]{
                {equalTo("ym:s:pvl<offline_region>Region<offline_window>Window"), anything()},
                {equalTo("ym:s:pvl<offline_point>Point<offline_window>Window"), anything()},
        });
    }

    @IgnoreParameters.Tag(name = "adfox")
    public static Collection<Object[]> ignoreParametersAdfox() {
        return asList(new Object[][]{
                {containsString("adfox"), anything()}
        });
    }
}
