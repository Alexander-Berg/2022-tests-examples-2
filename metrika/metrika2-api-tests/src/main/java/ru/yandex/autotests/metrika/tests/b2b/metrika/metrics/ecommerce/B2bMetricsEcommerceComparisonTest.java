package ru.yandex.autotests.metrika.tests.b2b.metrika.metrics.ecommerce;

import org.junit.Before;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

/**
 * Created by konkov on 28.09.2015.
 */
@Features({
        Requirements.Feature.DATA,
        Requirements.Feature.ECOMMERCE
})
@Stories({Requirements.Story.Report.Type.COMPARISON, Requirements.Story.Report.Parameter.METRICS})
@Title("B2B - метрики по визитам, eCommerce, метод COMPARISON")
public class B2bMetricsEcommerceComparisonTest extends BaseB2bMetricsEcommerceTest {
    @Before
    public void setup() {
        requestType = RequestTypes.COMPARISON;
        reportParameters = tail.append(new CommonReportParameters().withMetric(metricName));
    }
}
