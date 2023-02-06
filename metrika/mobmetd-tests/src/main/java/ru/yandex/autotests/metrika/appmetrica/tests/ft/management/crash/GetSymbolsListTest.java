package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.crash;

import java.util.Arrays;
import java.util.Collection;
import java.util.stream.Collectors;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Applications;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.crash.SymbolsTypeParam;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.crash.response.mappings.MappingsListing;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;

@Features(Requirements.Feature.Management.CRASH)
@Stories({
        Requirements.Story.Crash.ANDROID_SYMBOLS_LIST,
        Requirements.Story.Crash.ANDROID_SYMBOLS_MISSING_STAT,
        Requirements.Story.Crash.DSYM_LIST,
        Requirements.Story.Crash.DSYM_MISSING_STAT
})
@Title("Список загруженных и недостающих символов")
@RunWith(Parameterized.class)
public class GetSymbolsListTest {

    private final UserSteps userSteps = UserSteps.onTesting(Users.SUPER_LIMITED);

    private static final Long APP_ID = Applications.SAMPLE.get(Application.ID);

    @Parameter
    public SymbolsTypeParam symbolsType;

    @Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return Arrays.stream(SymbolsTypeParam.values())
                .map(symbolsType -> new Object[]{symbolsType})
                .collect(Collectors.toList());
    }

    @Before
    public void setup() {
        setCurrentLayerByApp(APP_ID);
    }

    @Test
    public void testListing() {
        MappingsListing actual = userSteps.onCommonSymbolsUploadSteps().getSymbolsList(APP_ID, symbolsType);
        assertThat("Возвращается список символов", actual, notNullValue());
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }

}
