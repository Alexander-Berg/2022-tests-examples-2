package ru.yandex.autotests.metrika.tests.ft.management.client_settings;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.ClientSettingsObjectWrapper;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.ClientSettings;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by omatikaya on 03.02.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.CLIENT_SETTINGS)
@Title("Проверка настройки пользовательских параметров новостной рассылки")
@RunWith(Parameterized.class)
public class ClientSettingsTest {
    private final static User USER = Users.USER_FOR_EMAIL_SUBSCRIPTION1;
    private final static User SUPER_USER = Users.SUPER_USER;

    private UserSteps user;
    private UserSteps superUser;

    private ClientSettings currentClientSettings;

    private ClientSettings returnedClientSettings;

    @Parameterized.Parameter()
    public ClientSettingsObjectWrapper initialClientSettings;

    @Parameterized.Parameter(1)
    public ClientSettingsObjectWrapper newClientSettings;

    @Parameterized.Parameter(2)
    public ClientSettingsObjectWrapper expectedClientSettings;

    @Parameterized.Parameters(name = "initial {0}, new {1}, expected {2}")
    public static List<Object> createParameters() {
        return asList(
                createClientSittingsParam(getDefaultClientSettings(), getDefaultClientSettings(), getDefaultClientSettings()),
                createClientSittingsParam(getDefaultClientSettings(), getClientSettingsTypeWithoutSubscriptionEmailsAndUnchecked(),
                        getClientSettingsTypeWithoutSubscriptionEmailsAndUnchecked()),
                createClientSittingsParam(getDefaultClientSettings(), getClientSettingsTypeWithSubscriptionEmails(),
                        getClientSettingsTypeWithSubscriptionEmails()),
                createClientSittingsParam(getDefaultClientSettings(), getClientSettingsTypeWithSubscriptionEmailsAndUnchecked(),
                        getClientSettingsTypeWithSubscriptionEmailsAndUnchecked()),

                createClientSittingsParam(getClientSettingsTypeWithoutSubscriptionEmailsAndUnchecked(),
                        getDefaultClientSettings(), getClientSettingsTypeWithoutSubscriptionEmailsAndUnchecked()),
                createClientSittingsParam(getClientSettingsTypeWithoutSubscriptionEmailsAndUnchecked(),
                        getClientSettingsTypeWithoutSubscriptionEmailsAndUnchecked(), getClientSettingsTypeWithoutSubscriptionEmailsAndUnchecked()),
                createClientSittingsParam(getClientSettingsTypeWithoutSubscriptionEmailsAndUnchecked(),
                        getClientSettingsTypeWithSubscriptionEmails(), getClientSettingsTypeWithSubscriptionEmailsAndUnchecked()),
                createClientSittingsParam(getClientSettingsTypeWithoutSubscriptionEmailsAndUnchecked(),
                        getClientSettingsTypeWithSubscriptionEmailsAndUnchecked(), getClientSettingsTypeWithSubscriptionEmailsAndUnchecked()),

                createClientSittingsParam(getClientSettingsTypeWithSubscriptionEmails(),
                        getDefaultClientSettings(), getDefaultClientSettings()),
                createClientSittingsParam(getClientSettingsTypeWithSubscriptionEmails(),
                        getClientSettingsTypeWithoutSubscriptionEmailsAndUnchecked(), getClientSettingsTypeWithoutSubscriptionEmailsAndUnchecked()),
                createClientSittingsParam(getClientSettingsTypeWithSubscriptionEmails(),
                        getClientSettingsTypeWithSubscriptionEmails(), getClientSettingsTypeWithSubscriptionEmails()),
                createClientSittingsParam(getClientSettingsTypeWithSubscriptionEmails(),
                        getClientSettingsTypeWithSubscriptionEmailsAndUnchecked(), getClientSettingsTypeWithSubscriptionEmailsAndUnchecked()),

                createClientSittingsParam(getClientSettingsTypeWithSubscriptionEmailsAndUnchecked(),
                        getDefaultClientSettings(), getClientSettingsTypeWithoutSubscriptionEmailsAndUnchecked()),
                createClientSittingsParam(getClientSettingsTypeWithSubscriptionEmailsAndUnchecked(),
                        getClientSettingsTypeWithoutSubscriptionEmailsAndUnchecked(), getClientSettingsTypeWithoutSubscriptionEmailsAndUnchecked()),
                createClientSittingsParam(getClientSettingsTypeWithSubscriptionEmailsAndUnchecked(),
                        getClientSettingsTypeWithSubscriptionEmails(), getClientSettingsTypeWithSubscriptionEmailsAndUnchecked()),
                createClientSittingsParam(getClientSettingsTypeWithSubscriptionEmailsAndUnchecked(),
                        getClientSettingsTypeWithSubscriptionEmailsAndUnchecked(), getClientSettingsTypeWithSubscriptionEmailsAndUnchecked())
        );
    }

    @Before
    public void setup() {
        user = new UserSteps().withUser(USER);
        superUser = new UserSteps().withUser(SUPER_USER);

        currentClientSettings = user.onManagementSteps().onClientSettingsSteps().getClientSettingsAndExpectSuccess();

        superUser.onInternalSteps().onClientSettingsSteps().rewriteClientSettingsAndExpectSuccess(initialClientSettings,
                USER.get(User.UID));

        returnedClientSettings = user.onManagementSteps().onClientSettingsSteps()
                .saveClientSettingsAndExpectSuccess(newClientSettings);
    }

    @Test
    public void checkAddedClientSettings() {
        assertThat("полученные настройки рассылки должны быть эквивалентны ожидаемым", returnedClientSettings,
                beanEquivalent(expectedClientSettings.get()));
    }

    @Test
    public void checkClientSettings() {
        returnedClientSettings = user.onManagementSteps().onClientSettingsSteps().getClientSettingsAndExpectSuccess();
        assertThat("возвращаемые настройки рассылки должны быть эквивалентны ожидаемым", returnedClientSettings,
                beanEquivalent(expectedClientSettings.get()));
    }
}
