package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.revenue;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.revenue.model.RevenueAppStoreCredentials;
import ru.yandex.metrika.mobmet.revenue.model.RevenueGooglePlayCredentials;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.*;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;

@Features(Requirements.Feature.Management.REVENUE)
@Stories({
        Requirements.Story.RevenueCredentials.EDIT
})
@Title("Редактирование данных о валидации покупок (негативный)")
public class RevenueCredentialsNegativeTest {

    private static final User USER = Users.SIMPLE_USER;
    private static UserSteps userSteps = UserSteps.onTesting(USER);

    private Long appId;

    @Before
    public void setup() {
        Application addedApplication = userSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
    }

    @Test
    public void invalidGooglePlayValue() {
        RevenueGooglePlayCredentials invalidValue = new RevenueGooglePlayCredentials()
                .withVerificationEnabled(true)
                .withPublicKey("abc");
        userSteps.onRevenueCredentialsSteps()
                .updateGooglePlayCredentialsAndExpectError(appId, invalidValue, INVALID_GOOGLE_PUBLIC_KEY);
    }

    @Test
    public void enableWithoutKey() {
        RevenueGooglePlayCredentials invalidValue = new RevenueGooglePlayCredentials().withVerificationEnabled(true);
        userSteps.onRevenueCredentialsSteps()
                .updateGooglePlayCredentialsAndExpectError(appId, invalidValue, GOOGLE_PUBLIC_KEY_REQUIRED);
    }

    @Test
    public void invalidAppStoreValue() {
        RevenueAppStoreCredentials invalidValue = new RevenueAppStoreCredentials()
                .withVerificationEnabled(true)
                .withSharedSecret("abc");
        userSteps.onRevenueCredentialsSteps()
                .updateAppStoreCredentialsAndExpectError(appId, invalidValue, INVALID_SHARED_SECRET);
    }

    @After
    public void teardown() {
        userSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
