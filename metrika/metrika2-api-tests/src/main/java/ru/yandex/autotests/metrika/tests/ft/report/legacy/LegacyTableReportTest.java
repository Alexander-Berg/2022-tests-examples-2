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

/**
 * Created by konkov on 02.12.2014.
 */
@Features(Requirements.Feature.LEGACY)
@Stories({Requirements.Story.Report.Parameter.PRESET, Requirements.Story.Report.Type.TABLE})
@Title("Legacy отчет 'таблица'")
@RunWith(Parameterized.class)
public class LegacyTableReportTest extends LegacyReportBaseTest {

    @Rule
    public ParametersIgnoreRule parametersIgnoreRule = new ParametersIgnoreRule();

    @Parameterized.Parameters(name = "{0} {1} {2}")
    public static Collection<Object[]> createParameters() {
        return user.onLegacyMetadataSteps().getPresetCounterGoalParameters(counters);
    }

    @Test
    @IgnoreParameters(reason = "METR-23070", tag = "METR-23070")
    public void legacyTableReportTest() {
        user.onLegacyReportSteps().getTableReportAndExpectSuccess(getReportParameters());
    }

}
