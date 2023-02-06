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
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.RevenueCreator.mask;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultRevenueAppStoreCredentials;

@Features(Requirements.Feature.Management.REVENUE)
@Stories({
        Requirements.Story.RevenueCredentials.EDIT
})
@Title("Редактирование данных о валидации покупок App Store")
public class RevenueAppStoreCredentialsTest {

    private static final User USER = Users.SIMPLE_USER;
    private static UserSteps userSteps = UserSteps.onTesting(USER);

    private Long appId;

    @Before
    public void setup() {
        Application addedApplication = userSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
    }

    @Test
    public void saveEnabled() {
        RevenueAppStoreCredentials input = getDefaultRevenueAppStoreCredentials();
        RevenueAppStoreCredentials expected = mask(input);
        RevenueAppStoreCredentials actual = userSteps.onRevenueCredentialsSteps().updateAppStoreCredentials(appId, input);
        assertThat("Ответ эквивалентен ожидаемому", actual, equivalentTo(expected));
    }

    @Test
    public void saveDisabled() {
        RevenueAppStoreCredentials input = getDefaultRevenueAppStoreCredentials().withVerificationEnabled(false);
        RevenueAppStoreCredentials expected = mask(input);
        RevenueAppStoreCredentials actual = userSteps.onRevenueCredentialsSteps().updateAppStoreCredentials(appId, input);
        assertThat("Ответ эквивалентен ожидаемому", actual, equivalentTo(expected));
    }

    @Test
    public void saveDisabledEmpty() {
        RevenueAppStoreCredentials input = new RevenueAppStoreCredentials().withVerificationEnabled(false);
        RevenueAppStoreCredentials expected = mask(input);
        RevenueAppStoreCredentials actual = userSteps.onRevenueCredentialsSteps().updateAppStoreCredentials(appId, input);
        assertThat("Ответ эквивалентен ожидаемому", actual, equivalentTo(expected));
    }

    @Test
    public void enable() {
        RevenueAppStoreCredentials input = getDefaultRevenueAppStoreCredentials().withVerificationEnabled(false);
        userSteps.onRevenueCredentialsSteps().updateAppStoreCredentials(appId, input);
        RevenueAppStoreCredentials actual = userSteps.onRevenueCredentialsSteps().enableAppStoreCredentials(appId);
        RevenueAppStoreCredentials expected = mask(input).withVerificationEnabled(true);
        assertThat("Ответ эквивалентен ожидаемому", actual, equivalentTo(expected));
    }

    @Test
    public void enableEmpty() {
        RevenueAppStoreCredentials actual = userSteps.onRevenueCredentialsSteps().enableAppStoreCredentials(appId);
        RevenueAppStoreCredentials expected = new RevenueAppStoreCredentials().withVerificationEnabled(true);
        assertThat("Ответ эквивалентен ожидаемому", actual, equivalentTo(expected));
    }

    @Test
    public void disable() {
        RevenueAppStoreCredentials input = getDefaultRevenueAppStoreCredentials();
        userSteps.onRevenueCredentialsSteps().updateAppStoreCredentials(appId, input);
        RevenueAppStoreCredentials actual = userSteps.onRevenueCredentialsSteps().disableAppStoreCredentials(appId);
        RevenueAppStoreCredentials expected = mask(input).withVerificationEnabled(false);
        assertThat("Ответ эквивалентен ожидаемому", actual, equivalentTo(expected));
    }

    @Test
    public void get() {
        RevenueAppStoreCredentials input = getDefaultRevenueAppStoreCredentials();
        userSteps.onRevenueCredentialsSteps().updateAppStoreCredentials(appId, input);
        RevenueAppStoreCredentials actual = userSteps.onRevenueCredentialsSteps().getAppStoreCredentials(appId);
        RevenueAppStoreCredentials expected = mask(input);
        assertThat("Ответ эквивалентен ожидаемому", actual, equivalentTo(expected));
    }

    @Test
    public void getEmpty() {
        RevenueAppStoreCredentials actual = userSteps.onRevenueCredentialsSteps().getAppStoreCredentials(appId);
        RevenueAppStoreCredentials expected = new RevenueAppStoreCredentials().withVerificationEnabled(false);
        assertThat("Ответ эквивалентен ожидаемому", actual, equivalentTo(expected));
    }

    @After
    public void teardown() {
        userSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
