package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.skad;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.cv.SKAdCVConfig;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultSKAdCVNotConfiguredConfig;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;

/**
 * Чтобы прочитать конфиг его нужно добавить.
 * Поэтому фактически основная проверка чтений идёт в {@link EditSKAdConversionValueConfigTest}.
 * Здесь только то, что там проверить нельзя из-за структуры теста.
 */
@Features(Requirements.Feature.Management.SKAD)
@Stories({
        Requirements.Story.SKAdConversionValue.INFO
})
@Title("Получение SKAd Conversion Value конфигурации")
public class GetSKAdConversionValueConfigTest {

    private static final User OWNER = Users.SIMPLE_USER;

    private final UserSteps user = UserSteps.onTesting(OWNER);

    private Long appId;

    @Before
    public void setup() {
        Application addedApplication = user.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
    }

    @Test
    public void emptyConfig() {
        SKAdCVConfig actual = user.onSKAdConversionValueSteps().getConfig(appId);
        assertThat("добавленный конфиг эквивалентен ожидаемому", actual, equivalentTo(defaultSKAdCVNotConfiguredConfig()));
    }

    @After
    public void teardown() {
        user.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
