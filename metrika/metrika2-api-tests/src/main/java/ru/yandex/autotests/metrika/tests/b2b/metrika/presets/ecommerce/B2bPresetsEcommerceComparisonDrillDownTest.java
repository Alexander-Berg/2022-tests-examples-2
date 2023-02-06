package ru.yandex.autotests.metrika.tests.b2b.metrika.presets.ecommerce;

import org.junit.Before;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonDrilldownReportParameters;
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
@Stories({Requirements.Story.Report.Type.COMPARISON_DRILLDOWN, Requirements.Story.Report.Parameter.PRESET})
@Title("B2B - пресеты по визитам, eCommerce, метод COMPARISON_DRILLDOWN")
public class B2bPresetsEcommerceComparisonDrillDownTest extends BaseB2bEcommercePresetsTest {
    @Before
    public void setup() {
        requestType = RequestTypes.COMPARISON_DRILLDOWN;

        reportParameters = new ComparisonDrilldownReportParameters()
                .withDate1_a(START_DATE)
                .withDate2_a(END_DATE)
                .withDate1_b(START_DATE)
                .withDate2_b(END_DATE)
                .withId(COUNTER.get(Counter.ID))
                .withPreset(preset)
                .withAccuracy("1");
    }
}
