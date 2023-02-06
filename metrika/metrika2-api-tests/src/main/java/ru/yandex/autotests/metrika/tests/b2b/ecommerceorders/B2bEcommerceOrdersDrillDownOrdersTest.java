package ru.yandex.autotests.metrika.tests.b2b.ecommerceorders;

import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum;
import ru.yandex.autotests.metrika.data.parameters.report.v1.DrillDownReportParameters;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bParticularTest;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.ECOMMERCE_TEST;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.sort.SortBuilder.sort;

/**
 * Created by konkov on 30.09.2015.
 */
@Features({
        Requirements.Feature.DATA,
        Requirements.Feature.ECOMMERCE
})
@Stories(Requirements.Story.Report.Type.ECOMMERCE_ORDERS)
@Title("B2B - отчет 'Содержимое заказов', drill down, заказы")
public class B2bEcommerceOrdersDrillDownOrdersTest extends BaseB2bParticularTest {
    @Parameterized.Parameters()
    public static Collection<Object[]> createParameters() {

        List<Object[]> params = new ArrayList<>();

        for (String currency : userOnTest.onMetadataSteps().getAvailableCurrencies()) {
            params.add(toArray(
                    createParams(String.format("Валюта %s", currency),
                            RequestTypes.ECOMMERCE_ORDERS_DRILLDOWN,
                            new DrillDownReportParameters()
                                    .withId(ECOMMERCE_TEST.get(ID))
                                    .withDimensions(userOnTest.onMetadataSteps().getDimensionsEcommerceOrders())
                                    .withMetrics(userOnTest.onMetadataSteps().getMetricsEcommerceOrders())
                                    .withSort(sort().by("ym:s:pProductPurchasedQuantity").descending().build())
                                    .withDate1(DateConstants.Ecommerce.START_DATE)
                                    .withDate2(DateConstants.Ecommerce.END_DATE),
                            makeParameters(ParametrizationTypeEnum.CURRENCY.getParameterName(), currency))));
        }


        return params;
    }
}
