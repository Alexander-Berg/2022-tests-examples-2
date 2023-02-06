package ru.yandex.autotests.metrika.tests.ft.report.ecommerceorders.drilldown;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.DrillDownReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

/**
 * Created by okunev on 09.09.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.Type.ECOMMERCE_ORDERS)
@Title("Отчет 'Drill down - содержимое заказов': список заказов")
public class EcommerceOrdersDrilldownDimensionsAndMetricsOrdersTest
        extends EcommerceOrdersDrilldownDimensionsAndMetricsBaseTest {

    @Override
    protected DrillDownReportParameters getReportParameters() {
        return new DrillDownReportParameters()
                .withId(COUNTER.get(Counter.ID))
                .withDimensions(DIMENSION_NAMES)
                .withMetrics(METRIC_NAMES)
                .withDate1(START_DATE)
                .withDate2(END_DATE);
    }

}
