package ru.yandex.autotests.metrika.tests.b2b.metrika.presets;

import org.junit.Before;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.data.metadata.v1.ParameterValues.getDefaults;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;

/**
 * Created by omaz on 12.12.14.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.Type.COMPARISON, Requirements.Story.Report.Parameter.PRESET})
@Title("B2B - пресеты по просмотрам и визитам, метод COMPARISON")
public class B2bPresetsComparisonTest extends BaseB2bPresetsTest {
    @Before
    public void setup() {
        requestType = RequestTypes.COMPARISON;
        reportParameters = makeParameters()
                .append(getDefaults(PRESET_TO_COUNTER.getOrDefault(preset.getPreset().getName(), COUNTER)).toFormParameters())
                .append(new ComparisonReportParameters()
                        .withDate1_a("12daysAgo")
                        .withDate1_b("11daysAgo")
                        .withDate2_a("11daysAgo")
                        .withDate2_b("10daysAgo")
                        .withId(getCounterId())
                        .withPreset(preset.getPreset().getName())
                        .withAccuracy("0.01"));
    }
}
