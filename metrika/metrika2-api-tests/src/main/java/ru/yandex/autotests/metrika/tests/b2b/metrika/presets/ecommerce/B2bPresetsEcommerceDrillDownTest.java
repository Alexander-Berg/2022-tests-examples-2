package ru.yandex.autotests.metrika.tests.b2b.metrika.presets.ecommerce;

import org.junit.Before;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.DrillDownReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;

/**
 * Created by konkov on 28.09.2015.
 */
@Features({
        Requirements.Feature.DATA,
        Requirements.Feature.ECOMMERCE
})
@Stories({Requirements.Story.Report.Type.DRILLDOWN, Requirements.Story.Report.Parameter.PRESET})
@Title("B2B - пресеты по визитам, eCommerce, метод DRILLDOWN")
public class B2bPresetsEcommerceDrillDownTest extends BaseB2bEcommercePresetsTest {
    @Before
    public void setup() {
        requestType = RequestTypes.DRILLDOWN;

        reportParameters = new DrillDownReportParameters()
                .withDate1(START_DATE)
                .withDate2(END_DATE)
                .withId(COUNTER.get(ID))
                .withPreset(preset)
                .withAccuracy("1");
    }
}
