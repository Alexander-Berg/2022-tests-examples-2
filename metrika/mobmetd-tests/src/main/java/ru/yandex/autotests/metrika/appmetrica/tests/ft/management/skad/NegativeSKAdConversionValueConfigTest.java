package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.skad;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.skad.SKAdConfigParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.cv.SKAdCVConfig;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.*;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultSKAdCVRevenueConfig;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;

@Features(Requirements.Feature.Management.SKAD)
@Stories({
        Requirements.Story.SKAdConversionValue.EDIT
})
@Title("Получение SKAd Conversion Value конфигурации (негативный)")
public class NegativeSKAdConversionValueConfigTest {

    private static final User OWNER = Users.SIMPLE_USER;

    private final UserSteps user = UserSteps.onTesting(OWNER);

    private Long appId;

    @Before
    public void setup() {
        Application addedApplication = user.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
    }

    @Test
    public void missingType() {
        SKAdCVConfig config = new SKAdCVConfig().withModelType(null);
        user.onSKAdConversionValueSteps()
                .updateConfigAndExpectError(appId, config, MUST_NOT_BE_NULL, new SKAdConfigParameters().forceBundles());
    }

    @Test
    public void missingEvents() {
        SKAdCVConfig config = defaultSKAdCVRevenueConfig().withRevenueModel(null);
        user.onSKAdConversionValueSteps()
                .updateConfigAndExpectError(appId, config, SKAD_CONVERSION_VALUE_MODEL_NOT_SET,
                        new SKAdConfigParameters().forceBundles());
    }

    @Test
    public void unknownBundleIds() {
        user.onSKAdConversionValueSteps()
                .updateConfigAndExpectError(appId, defaultSKAdCVRevenueConfig(), SKAD_CONVERSION_VALUE_UNKNOWN_BUNDLE_IDS);
    }

    @After
    public void teardown() {
        user.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
