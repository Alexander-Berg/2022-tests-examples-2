package ru.yandex.autotests.metrika.tests.b2b.metrika.dimensions.ecommerce;

import org.junit.Before;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
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
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.DIMENSIONS})
@Title("B2B - измерения по визитам, eCommerce, метод TABLE")
public class B2bDimensionsEcommerceTableTest extends BaseB2bDimensionsEcommerceTest {
    @Before
    public void setup() {
        requestType = RequestTypes.TABLE;

        reportParameters = new TableReportParameters()
                .withDate1(START_DATE)
                .withDate2(END_DATE)
                .withId(COUNTER.get(Counter.ID))
                .withMetric(metricName)
                .withDimension(dimensionName)
                .withAccuracy("1");
    }
}
