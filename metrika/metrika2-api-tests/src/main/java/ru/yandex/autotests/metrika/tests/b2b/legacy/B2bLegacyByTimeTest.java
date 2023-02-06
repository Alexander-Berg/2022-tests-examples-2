package ru.yandex.autotests.metrika.tests.b2b.legacy;

import org.junit.Before;
import org.junit.Rule;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.commons.rules.ParametersIgnoreRule;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static org.apache.commons.lang3.StringUtils.EMPTY;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SHATURA_COM;

/**
 * Created by konkov on 10.08.2015.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.Parameter.PRESET, Requirements.Story.Report.Type.BYTIME})
@Title("B2B - Legacy отчет 'по времени'")
public class B2bLegacyByTimeTest extends BaseB2bLegacyTest {

    @Rule
    public ParametersIgnoreRule parametersIgnoreRule = new ParametersIgnoreRule();

    @Parameterized.Parameters(name = "{0} {1} {2}")
    public static Collection<Object[]> createParameters() {
        return userOnTest.onLegacyMetadataSteps().getPresetCounterGoalParameters(counters);
    }

    @Before
    public void setup() {
        requestType = RequestTypes.LEGACY_BY_TIME;

        reportParameters = getReportParameters();
    }

    @IgnoreParameters.Tag(name = "METR-39392")
    public static Collection<Object[]> ignoreParametersMetr39392() {
        return asList(new Object[][]{
                {"robots_all", SENDFLOWERS_RU, EMPTY},
                {"robots_all", SHATURA_COM, EMPTY}
        });
    }
}
