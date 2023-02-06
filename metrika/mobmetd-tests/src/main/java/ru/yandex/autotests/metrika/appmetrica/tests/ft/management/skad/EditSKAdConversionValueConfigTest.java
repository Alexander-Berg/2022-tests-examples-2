package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.skad;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.skad.SKAdConfigParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.SKAdConversionValueConfigWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.cv.SKAdCVConfig;
import ru.yandex.metrika.mobmet.model.cv.SKAdCVConversionModelEvent;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Arrays;
import java.util.Collection;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.*;
import static ru.yandex.autotests.metrika.appmetrica.wrappers.SKAdConversionValueConfigWrapper.wrap;
import static ru.yandex.metrika.segments.apps.bundles.AppEventType.*;

@Features(Requirements.Feature.Management.SKAD)
@Stories({
        Requirements.Story.SKAdConversionValue.INFO,
        Requirements.Story.SKAdConversionValue.EDIT
})
@Title("Редактирование SKAd Conversion Value конфигурации")
@RunWith(Parameterized.class)
public class EditSKAdConversionValueConfigTest {

    private static final User OWNER = Users.SIMPLE_USER;

    private final UserSteps user = UserSteps.onTesting(OWNER);

    @Parameterized.Parameter
    public SKAdConversionValueConfigWrapper initialConfig;

    @Parameterized.Parameter(1)
    public SKAdConversionValueConfigWrapper configToAdd;

    @Parameterized.Parameter(2)
    public SKAdConversionValueConfigWrapper expectedConfig;

    private Long appId;

    @Parameterized.Parameters(name = "Исходное состояние {0}. Ожидаемое состояние {2}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                param(null, defaultSKAdCVNotConfiguredConfig()),
                param(defaultSKAdCVNotConfiguredConfig(), defaultSKAdCVNotConfiguredConfig()),
                param(null, defaultSKAdCVRevenueConfig()),
                param(null, defaultSKAdCVConversionConfig()),
                param(null, defaultSKAdCVEngagementConfig()),
                param(defaultSKAdCVRevenueConfig(), defaultSKAdCVConversionConfig()),
                param(defaultSKAdCVConversionConfig(), defaultSKAdCVRevenueConfig()),
                param(defaultSKAdCVConversionConfig(), defaultSKAdCVEngagementConfig()),
                param(defaultSKAdCVConversionConfig(), defaultSKAdCVNotConfiguredConfig()),
                param(defaultSKAdCVConversionConfig(), fullConversionConfig()));
    }

    @Before
    public void setup() {
        Application addedApplication = user.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
        if (initialConfig.getConfig() != null) {
            user.onSKAdConversionValueSteps()
                    .updateConfig(appId, initialConfig.getConfig(), new SKAdConfigParameters().forceBundles());
        }
    }

    @Test
    public void checkConfigUpdate() {
        SKAdCVConfig updateResponse = user.onSKAdConversionValueSteps()
                .updateConfig(appId, configToAdd.getConfig(), new SKAdConfigParameters().forceBundles());
        assumeThat("добавленный конфиг эквивалентен ожидаемому", updateResponse, equivalentTo(expectedConfig.getConfig()));

        SKAdCVConfig getResponse = user.onSKAdConversionValueSteps().getConfig(appId);
        assertThat("прочитанный конфиг эквивалентен ожидаемому", getResponse, equivalentTo(expectedConfig.getConfig()));
    }

    @After
    public void teardown() {
        user.onSKAdConversionValueSteps().updateConfig(appId, defaultSKAdCVNotConfiguredConfig());
        user.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    private static SKAdCVConfig fullConversionConfig() {
        SKAdCVConfig config = defaultSKAdCVConversionConfig();
        config.getConversionModel().setEvents(Arrays.asList(
                new SKAdCVConversionModelEvent().withEventType(EVENT_CLIENT).withEventName("a"),
                new SKAdCVConversionModelEvent().withEventType(EVENT_CLIENT).withEventName("b"),
                new SKAdCVConversionModelEvent().withEventType(ECOMMERCE).withEventSubtype("show_screen"),
                new SKAdCVConversionModelEvent().withEventType(EVENT_REVENUE),
                new SKAdCVConversionModelEvent().withEventType(EVENT_CLIENT).withEventName("c"),
                new SKAdCVConversionModelEvent().withEventType(EVENT_CLIENT).withEventName("d")));
        return config;
    }

    private static Object[] param(SKAdCVConfig initial, SKAdCVConfig target) {
        return toArray(wrap(initial), wrap(target), wrap(target));
    }
}
