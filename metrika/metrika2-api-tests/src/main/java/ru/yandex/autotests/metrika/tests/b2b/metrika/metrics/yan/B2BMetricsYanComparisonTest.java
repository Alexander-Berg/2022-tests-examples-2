package ru.yandex.autotests.metrika.tests.b2b.metrika.metrics.yan;

import org.junit.Before;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

@Features({
        Requirements.Feature.DATA,
        Requirements.Feature.YAN
})
@Stories({Requirements.Story.Report.Type.COMPARISON, Requirements.Story.Report.Parameter.METRICS})
@Title("B2B - метрики по визитам, РСЯ, метод COMPARISON")
public class B2BMetricsYanComparisonTest extends BaseB2bMetricsYanTest {
    @Before
    public void setup() {
        requestType = RequestTypes.COMPARISON;
        reportParameters = tail.append(new CommonReportParameters()
                .withMetric(metricName)
                .withAccuracy("0.1"));
    }
}
