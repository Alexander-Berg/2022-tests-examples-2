package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.revenue;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.revenue.model.RevenueGooglePlayCredentials;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.RevenueCreator.mask;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultRevenueGoogleCredentials;

@Features(Requirements.Feature.Management.REVENUE)
@Stories({
        Requirements.Story.RevenueCredentials.EDIT
})
@Title("Редактирование данных о валидации покупок Google Play")
public class RevenueGooglePlayCredentialsTest {

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
        RevenueGooglePlayCredentials input = getDefaultRevenueGoogleCredentials();
        RevenueGooglePlayCredentials expected = mask(input);
        RevenueGooglePlayCredentials actual = userSteps.onRevenueCredentialsSteps().updateGooglePlayCredentials(appId, input);
        assertThat("Ответ эквивалентен ожидаемому", actual, equivalentTo(expected));
    }

    @Test
    public void saveDisabled() {
        RevenueGooglePlayCredentials input = getDefaultRevenueGoogleCredentials().withVerificationEnabled(false);
        RevenueGooglePlayCredentials expected = mask(input);
        RevenueGooglePlayCredentials actual = userSteps.onRevenueCredentialsSteps().updateGooglePlayCredentials(appId, input);
        assertThat("Ответ эквивалентен ожидаемому", actual, equivalentTo(expected));
    }

    @Test
    public void saveDisabledEmpty() {
        RevenueGooglePlayCredentials input = new RevenueGooglePlayCredentials().withVerificationEnabled(false);
        RevenueGooglePlayCredentials expected = mask(input);
        RevenueGooglePlayCredentials actual = userSteps.onRevenueCredentialsSteps().updateGooglePlayCredentials(appId, input);
        assertThat("Ответ эквивалентен ожидаемому", actual, equivalentTo(expected));
    }

    @Test
    public void enable() {
        RevenueGooglePlayCredentials input = getDefaultRevenueGoogleCredentials().withVerificationEnabled(false);
        userSteps.onRevenueCredentialsSteps().updateGooglePlayCredentials(appId, input);
        RevenueGooglePlayCredentials actual = userSteps.onRevenueCredentialsSteps().enableGooglePlayCredentials(appId);
        RevenueGooglePlayCredentials expected = mask(input).withVerificationEnabled(true);
        assertThat("Ответ эквивалентен ожидаемому", actual, equivalentTo(expected));
    }

    @Test
    public void disable() {
        RevenueGooglePlayCredentials input = getDefaultRevenueGoogleCredentials();
        userSteps.onRevenueCredentialsSteps().updateGooglePlayCredentials(appId, input);
        RevenueGooglePlayCredentials actual = userSteps.onRevenueCredentialsSteps().disableGooglePlayCredentials(appId);
        RevenueGooglePlayCredentials expected = mask(input).withVerificationEnabled(false);
        assertThat("Ответ эквивалентен ожидаемому", actual, equivalentTo(expected));
    }

    @Test
    public void get() {
        RevenueGooglePlayCredentials input = getDefaultRevenueGoogleCredentials();
        userSteps.onRevenueCredentialsSteps().updateGooglePlayCredentials(appId, input);
        RevenueGooglePlayCredentials actual = userSteps.onRevenueCredentialsSteps().getGooglePlayCredentials(appId);
        RevenueGooglePlayCredentials expected = mask(input);
        assertThat("Ответ эквивалентен ожидаемому", actual, equivalentTo(expected));
    }

    @Test
    public void getEmpty() {
        RevenueGooglePlayCredentials actual = userSteps.onRevenueCredentialsSteps().getGooglePlayCredentials(appId);
        RevenueGooglePlayCredentials expected = new RevenueGooglePlayCredentials().withVerificationEnabled(false);
        assertThat("Ответ эквивалентен ожидаемому", actual, equivalentTo(expected));
    }

    @After
    public void teardown() {
        userSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
