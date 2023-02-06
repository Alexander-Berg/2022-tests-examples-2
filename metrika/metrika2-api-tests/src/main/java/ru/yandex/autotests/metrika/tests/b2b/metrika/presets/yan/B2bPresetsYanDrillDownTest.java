package ru.yandex.autotests.metrika.tests.b2b.metrika.presets.yan;

import org.junit.Before;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.DrillDownReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;

@Features({
        Requirements.Feature.DATA,
        Requirements.Feature.YAN
})
@Stories({Requirements.Story.Report.Type.DRILLDOWN, Requirements.Story.Report.Parameter.PRESET})
@Title("B2B - пресеты по визитам, РСЯ, метод DRILLDOWN")
public class B2bPresetsYanDrillDownTest extends BaseB2bYanPresetsTest {
    @Before
    public void setup() {
        requestType = RequestTypes.DRILLDOWN;

        reportParameters = new DrillDownReportParameters()
                .withDate1(START_DATE)
                .withDate2(END_DATE)
                .withId(COUNTER.get(ID))
                .withPreset(preset)
                .withAccuracy("0.1");
    }
}
