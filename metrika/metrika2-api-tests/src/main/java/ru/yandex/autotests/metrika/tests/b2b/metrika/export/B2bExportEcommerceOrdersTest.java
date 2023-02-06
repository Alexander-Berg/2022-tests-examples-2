package ru.yandex.autotests.metrika.tests.b2b.metrika.export;

import org.junit.Before;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.ECOMMERCE_TEST;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.ECOMMERCE_ORDERS_TABLE;

/**
 * Created by sourx on 29/06/16.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Format.CSV,
        Requirements.Story.Report.Format.XLSX})
@Title("B2B - Экспорт отчета 'Содержимое заказов' в excel")
public class B2bExportEcommerceOrdersTest extends BaseB2bExportTest {
    private static final Counter COUNTER = ECOMMERCE_TEST;
    private static final String START_DATE = DateConstants.Ecommerce.START_DATE;
    private static final String END_DATE = DateConstants.Ecommerce.END_DATE;

    @Before
    public void setup() {
        requestType = ECOMMERCE_ORDERS_TABLE;
        reportParameters = new TableReportParameters()
                .withId(COUNTER.get(ID))
                .withDimensions(userOnTest.onMetadataSteps().getDimensionsEcommerceOrders())
                .withMetrics(userOnTest.onMetadataSteps().getMetricsEcommerceOrders())
                .withDate1(START_DATE)
                .withDate2(END_DATE);
    }
}
