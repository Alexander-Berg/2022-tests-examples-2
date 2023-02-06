package ru.yandex.autotests.metrika.tests.b2b.metrika.presets.advertising;

import org.junit.Before;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonDrilldownReportParameters;
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
@Stories({Requirements.Story.Report.Type.COMPARISON_DRILLDOWN, Requirements.Story.Report.Parameter.PRESET})
@Title("B2B - пресеты по кликам Директа, метод COMPARISON_DRILLDOWN")
public class B2bPresetsAdvertisingComparisonDrillDownTest extends BaseB2bAdvertisingPresetsTest {
    @Before
    public void setup() {
        requestType = RequestTypes.COMPARISON_DRILLDOWN;

        reportParameters = new FreeFormParameters()
                .append(new ComparisonDrilldownReportParameters()
                        .withDate1_a(START_DATE)
                        .withDate2_a(END_DATE)
                        .withDate1_b(START_DATE)
                        .withDate2_b(END_DATE)
                        .withId(COUNTER.get(Counter.ID))
                        .withPreset(preset)
                        .withDirectClientLogins(directClientLogins))
                .append(parametrization().withAttribution(attribution));
    }
}
