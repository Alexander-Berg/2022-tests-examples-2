package ru.yandex.autotests.metrika.tests.b2b.metrika.metrics.advertising;

import org.junit.Before;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

/**
 * Created by konkov on 30.07.2015.
 */
@Features({
        Requirements.Feature.DATA,
        Requirements.Feature.ADVERTISING
})
@Stories({Requirements.Story.Report.Type.DRILLDOWN, Requirements.Story.Report.Parameter.METRICS})
@Title("B2B - метрики по кликам Директа, метод DRILLDOWN")
public class B2bMetricsAdvertisingDrillDownTest extends BaseB2bMetricsAdvertisingTest {

    @Before
    public void setup() {
        requestType = RequestTypes.DRILLDOWN;
        reportParameters = tail.append(new CommonReportParameters().withMetric(metricName));
    }
}
