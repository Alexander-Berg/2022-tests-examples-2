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

import static java.util.Arrays.asList;
import static java.util.Collections.singletonList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.ECOMMERCE_TEST;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;

/**
 * Created by konkov on 30.09.2015.
 */
@Features({
        Requirements.Feature.DATA,
        Requirements.Feature.ECOMMERCE
})
@Stories(Requirements.Story.Report.Type.ECOMMERCE_ORDERS)
@Title("B2B - отчет 'Содержимое заказов', drill down, товары заказа")
public class B2bEcommerceOrdersDrillDownGoodsTest extends BaseB2bParticularTest {

    private static final List<String> orders = asList("3001", "3002", "L2001", "L2003");

    @Parameterized.Parameters()
    public static Collection<Object[]> createParameters() {

        List<Object[]> params = new ArrayList<>();

        for (String order : orders) {
            for (String currency : userOnTest.onMetadataSteps().getAvailableCurrencies()) {
                params.add(toArray(
                        createParams(String.format("товары заказа %s, валюта %s", order, currency),
                                RequestTypes.ECOMMERCE_ORDERS_DRILLDOWN,
                                new DrillDownReportParameters()
                                        .withId(ECOMMERCE_TEST.get(ID))
                                        .withDimensions(userOnTest.onMetadataSteps().getDimensionsEcommerceOrders())
                                        .withMetrics(userOnTest.onMetadataSteps().getMetricsEcommerceOrders())
                                        .withDate1(DateConstants.Ecommerce.START_DATE)
                                        .withDate2(DateConstants.Ecommerce.END_DATE)
                                        .withParentIds(singletonList(order)),
                                makeParameters(ParametrizationTypeEnum.CURRENCY.getParameterName(), currency))));
            }
        }

        return params;
    }
}
