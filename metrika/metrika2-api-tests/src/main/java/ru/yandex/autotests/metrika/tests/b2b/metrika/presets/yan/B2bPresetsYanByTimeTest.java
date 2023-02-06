package ru.yandex.autotests.metrika.tests.b2b.metrika.presets.yan;

import org.junit.Before;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.BytimeReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

@Features({
        Requirements.Feature.DATA,
        Requirements.Feature.YAN
})
@Stories({Requirements.Story.Report.Type.BYTIME, Requirements.Story.Report.Parameter.PRESET})
@Title("B2B - пресеты по визитам, РСЯ, метод BY_TIME")
public class B2bPresetsYanByTimeTest extends BaseB2bYanPresetsTest {
    @Before
    public void setup() {
        requestType = RequestTypes.BY_TIME;

        reportParameters = new BytimeReportParameters()
                .withDate1(START_DATE)
                .withDate2(END_DATE)
                .withId(COUNTER.get(Counter.ID))
                .withPreset(preset)
                .withAccuracy("0.1");
    }
}
