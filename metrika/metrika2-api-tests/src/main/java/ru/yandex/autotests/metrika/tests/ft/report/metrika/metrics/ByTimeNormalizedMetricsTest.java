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
import static org.hamcrest.Matchers.hasEntry;
import static ru.yandex.autotests.metrika.filters.MetricExpression.metricFunction;
import static ru.yandex.autotests.metrika.matchers.NormalizedMatchers.areNormalized;
import static ru.yandex.autotests.metrika.utils.AllureUtils.addTestParameter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.Lists2.transpose;

/**
 * Created by konkov on 20.08.2014.
 */
@Features({Requirements.Feature.REPORT})
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.METRICS})
@Title("Отчет 'по времени': метрики в процентах")
@RunWith(Parameterized.class)
public class ByTimeNormalizedMetricsTest extends ByTimeMetricsTest {

    @Before
    public void setup() {
        ImmutableList<String> metrics = ImmutableList.of(metricName, metricFunction("normBytime", metricName));
        addTestParameter("Метрики", metrics.toString());
        addTestParameter("Остальное", tail.toString());
        result = user.onReportSteps().getBytimeReportAndExpectSuccess(
                tail,
                new CommonReportParameters().withMetrics(metrics));
    }

    /**
     * этот код не работает для dimensions=ym:s:date
     */
    @Test
    @IgnoreParameters(reason = "нормализация не работает для ym:s:date", tag = "time")
    @IgnoreParameters(reason = "METR-23460", tag = "pvl")
    @IgnoreParameters(reason = "METR-31915", tag = "adfox")
    public void checkMetricValues() {
        // в запросе две метрики, поэтому metrics - это список списков длиной два, в которых внутри список точек.
        List<List<List<Double>>> metrics = user.onResultSteps().getMetrics(result);
        // значение[метрика][ключ группировки][момент времени]
        List<List<List<Double>>> transposed = transpose(metrics);
        // значение[метрика][момент времени]
        List<List<Double>> rawMetric = transposed.get(0);
        List<List<Double>> normalizedMetric = transposed.get(1);
        List<Double> rawTotals = result.getTotals().get(0);

        assertThat("метрика отнормирована корректно", normalizedMetric, areNormalized(rawMetric, rawTotals));
    }

    @IgnoreParameters.Tag(name = "time")
    public static Collection<Object[]> ignoreParameters() {
        return asList(new Object[][]{
                {anything(), hasEntry("dimensions", "ym:s:date")}
        });
    }

    @IgnoreParameters.Tag(name = "pvl")
    public static Collection<Object[]> ignoreParametersPvl() {
        return asList(new Object[][]{
                {equalTo("ym:s:pvl<offline_region>Region<offline_window>Window"), anything()},
                {equalTo("ym:s:pvl<offline_point>Point<offline_window>Window"), anything()},
                {equalTo("ym:s:yanVisibility"), anything()},
        });
    }


    @IgnoreParameters.Tag(name = "adfox")
    public static Collection<Object[]> ignoreParametersAdfox() {
        return asList(new Object[][]{
                {containsString("adfox"), anything()}
        });
    }
}
