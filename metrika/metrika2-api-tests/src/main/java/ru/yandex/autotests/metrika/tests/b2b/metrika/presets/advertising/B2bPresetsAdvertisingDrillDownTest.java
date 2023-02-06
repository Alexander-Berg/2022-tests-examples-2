package ru.yandex.autotests.metrika.tests.b2b.metrika.presets.advertising;

import org.junit.Before;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.DrillDownReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.data.parameters.report.v1.ParametrizationParameters.parametrization;

/**
 * Created by konkov on 30.07.2015.
 */
@Features({
        Requirements.Feature.DATA,
        Requirements.Feature.ADVERTISING
})
@Stories({Requirements.Story.Report.Type.DRILLDOWN, Requirements.Story.Report.Parameter.PRESET})
@Title("B2B - пресеты по кликам Директа, метод DRILLDOWN")
public class B2bPresetsAdvertisingDrillDownTest extends BaseB2bAdvertisingPresetsTest {
    @Before
    public void setup() {
        requestType = RequestTypes.DRILLDOWN;

        reportParameters = new FreeFormParameters()
                .append(new DrillDownReportParameters()
                        .withDate1(START_DATE)
                        .withDate2(END_DATE)
                        .withId(COUNTER.get(Counter.ID))
                        .withPreset(preset)
                        .withDirectClientLogins(directClientLogins))
                .append(parametrization().withAttribution(attribution));
    }
}
