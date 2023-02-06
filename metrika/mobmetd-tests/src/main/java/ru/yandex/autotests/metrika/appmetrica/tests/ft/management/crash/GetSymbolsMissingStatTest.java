package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.crash;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Applications;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.crash.ReportGroup;
import ru.yandex.autotests.metrika.appmetrica.parameters.crash.SymbolsTypeParam;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.metrika.mobmet.crash.response.mappings.MissingMappingsStat;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;

@Features(Requirements.Feature.Management.CRASH)
@Stories({
        Requirements.Story.Crash.DSYM_MISSING_STAT,
        Requirements.Story.Crash.ANDROID_SYMBOLS_MISSING_STAT
})
@Title("Статистика о недостающих символах")
@RunWith(Parameterized.class)
public class GetSymbolsMissingStatTest {

    private final UserSteps userSteps = UserSteps.onTesting(Users.SUPER_LIMITED);

    private static final Long APP_ID = Applications.SAMPLE.get(Application.ID);

    @Parameterized.Parameter
    public ReportGroup report;

    @Parameterized.Parameter(1)
    public SymbolsTypeParam symbolsType;

    @Parameterized.Parameters(name = "Report: {0}. SymbolsType: {1}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .values(ReportGroup.values())
                .values(SymbolsTypeParam.values())
                .build();
    }

    @Before
    public void setup() {
        setCurrentLayerByApp(APP_ID);
    }

    @Test
    public void testMissingSymbolsStat() {
        MissingMappingsStat actual = userSteps.onCommonSymbolsUploadSteps().getMissingSymbolsStat(report, APP_ID, symbolsType);
        assertThat("Возвращается статистика о недостающих символах файлах", actual, notNullValue());
    }

    @Test
    public void testMissingCrashStatForCrashGroup() {
        MissingMappingsStat actual = userSteps.onCommonSymbolsUploadSteps().getMissingSymbolsStat(report, APP_ID, symbolsType, TestData.getCrashGroupId());
        assertThat("Возвращается статистика о недостающих символах для крэш-группы", actual, notNullValue());
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }

}
