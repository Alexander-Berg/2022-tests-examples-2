package ru.yandex.autotests.metrika.tests.b2b.metrika.metrics.crossdeviceattribution;

import org.junit.Before;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

@Features({
        Requirements.Feature.DATA,
        Requirements.Feature.CROSS_DEVICE_ATTRIBUTION
})
@Stories({Requirements.Story.Report.Type.BYTIME, Requirements.Story.Report.Parameter.METRICS})
@Title("B2B - метрики по визитам, аттрибуции кросс-девайс, метод BY_TIME")
public class B2BMetricsCrossDeviceAttributionByTimeTest extends BaseB2bMetricsCrossDeviceAttributionTest {
    @Before
    public void setup() {
        requestType = RequestTypes.BY_TIME;
        reportParameters = tail.append(new CommonReportParameters()
                .withMetric(metricName)
                .withAccuracy("0.1"));
    }
}
