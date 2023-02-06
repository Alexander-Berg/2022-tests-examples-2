package ru.yandex.autotests.metrika.tests.ft.report.legacy;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.commons.rules.ParametersIgnoreRule;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static org.apache.commons.lang3.StringUtils.EMPTY;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SHATURA_COM;

/**
 * Created by konkov on 02.12.2014.
 */
@Features(Requirements.Feature.LEGACY)
@Stories({Requirements.Story.Report.Parameter.PRESET, Requirements.Story.Report.Type.BYTIME})
@Title("Legacy отчет 'по времени'")
@RunWith(Parameterized.class)
public class LegacyByTimeReportTest extends LegacyReportBaseTest {

    @Rule
    public ParametersIgnoreRule parametersIgnoreRule = new ParametersIgnoreRule();

    @Parameterized.Parameters(name = "{0} {1} {2}")
    public static Collection createParameters() {
        return user.onLegacyMetadataSteps().getPresetCounterGoalParameters(counters);
    }

    @Test
    @IgnoreParameters(reason = "METR-23070", tag = "METR-23070")
    public void legacyByTimeReportTest() {
        user.onLegacyReportSteps().getBytimeReportAndExpectSuccess(getReportParameters());
    }

    @IgnoreParameters.Tag(name = "METR-23070")
    public static Collection<Object[]> ignoreParametersMetr23070() {
        return asList(new Object[][]{
                {"robots_all", SENDFLOWERS_RU, EMPTY},
                {"robots_all", SHATURA_COM, EMPTY}
        });
    }
}
