package ru.yandex.autotests.advapi.api.tests.b2b.reports.presets;

import org.junit.Before;
import ru.yandex.autotests.advapi.api.tests.utils.Requirements;
import ru.yandex.autotests.advapi.data.common.RequestTypes;
import ru.yandex.autotests.advapi.parameters.DrillDownReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.advapi.data.common.Campaign.YNDX_MARKET_W;

/**
 * Created by omaz on 12.12.14.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.Type.DRILLDOWN, Requirements.Story.Report.Parameter.PRESET})
@Title("B2B - пресеты по просмотрам и визитам, метод DRILLDOWN")
public class B2bPresetsDrillDownTest extends BaseB2bPresetsTest {
    @Before
    public void setup() {
        requestType = RequestTypes.DRILLDOWN;

        reportParameters = new DrillDownReportParameters()
                .withDate1(YNDX_MARKET_W.date1)
                .withDate2(YNDX_MARKET_W.date2)
                .withId(YNDX_MARKET_W.id)
                .withPreset(preset.getPreset().getName())
                .withGoalId(YNDX_MARKET_W.goalId)
                .withAccuracy("0.1");
    }
}
