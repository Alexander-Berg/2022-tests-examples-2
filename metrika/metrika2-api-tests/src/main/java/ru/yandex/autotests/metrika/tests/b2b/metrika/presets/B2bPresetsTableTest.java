package ru.yandex.autotests.metrika.tests.b2b.metrika.presets;

import org.junit.Before;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.data.metadata.v1.ParameterValues.getDefaults;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;

/**
 * Created by omaz on 12.12.14.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.PRESET})
@Title("B2B - пресеты по просмотрам и визитам, метод TABLE")
public class B2bPresetsTableTest extends BaseB2bPresetsTest {
    @Before
    public void setup() {
        requestType = RequestTypes.TABLE;
        reportParameters = makeParameters()
                .append(getDefaults(PRESET_TO_COUNTER.getOrDefault(preset.getPreset().getName(), COUNTER)).toFormParameters())
                .append(new TableReportParameters()
                        .withDate1("10daysAgo")
                        .withDate2("10daysAgo")
                        .withId(getCounterId())
                        .withPreset(preset.getPreset().getName())
                        .withAccuracy("0.1"));
    }
}
