package ru.yandex.autotests.advapi.api.tests.b2b.reports.metrics;

import org.junit.Before;
import ru.yandex.autotests.advapi.api.tests.utils.Requirements;
import ru.yandex.autotests.advapi.data.common.RequestTypes;
import ru.yandex.autotests.advapi.parameters.CommonReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

/**
 * Created by omaz on 12.12.14.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.Type.BYTIME, Requirements.Story.Report.Parameter.METRICS})
@Title("B2B - метрики по просмотрам и визитам, метод BY_TIME")
public class B2bMetricsByTimeTest extends BaseB2bMetricsTest {
    @Before
    public void setup() {
        requestType = RequestTypes.BY_TIME;
        reportParameters = tail.append(new CommonReportParameters().withMetric(metricName));
    }
}
