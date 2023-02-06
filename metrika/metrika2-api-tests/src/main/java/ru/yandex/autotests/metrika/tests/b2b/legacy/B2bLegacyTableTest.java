package ru.yandex.autotests.metrika.tests.b2b.legacy;

import org.junit.Before;
import org.junit.Rule;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.rules.ParametersIgnoreRule;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.sort.SortBuilder.sort;

/**
 * Created by konkov on 10.08.2015.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.Parameter.PRESET, Requirements.Story.Report.Type.BYTIME})
@Title("B2B - Legacy отчет 'таблица'")
public class B2bLegacyTableTest extends BaseB2bLegacyTest {

    @Rule
    public ParametersIgnoreRule parametersIgnoreRule = new ParametersIgnoreRule();

    @Parameterized.Parameters(name = "{0} {1} {2}")
    public static Collection<Object[]> createParameters() {
        return userOnTest.onLegacyMetadataSteps().getPresetCounterGoalParameters(counters);
    }

    @Before
    public void setup() {
        requestType = RequestTypes.LEGACY_TABLE;

        reportParameters = getReportParameters();
    }

    @Override
    protected IFormParameters getReportParameters() {
        return makeParameters()
                .append(super.getReportParameters())
                .append(new CommonReportParameters()
                        .withSort(sort().by(preset.getPreset().getDimensions().get(0)).build()));
    }
}
