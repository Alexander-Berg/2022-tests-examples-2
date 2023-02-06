package ru.yandex.autotests.metrika.tests.ft.internal;

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

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by omatikaya on 17.03.17.
 */
@Features(Requirements.Feature.INTERNAL)
@Stories(Requirements.Story.Internal.CLIENT_SETTINGS)
@Title("Проверка перезаписи пользовательских параметров новостной рассылки")
@RunWith(Parameterized.class)
public class RewriteClientSettingsTest {
    private final static User USER = Users.USER_FOR_EMAIL_SUBSCRIPTION2;
    private final static User SUPER_USER = Users.SUPER_USER;

    private UserSteps user;
    private UserSteps superUser;

    private ClientSettings returnedClientSettings;

    @Parameterized.Parameter()
    public ClientSettingsObjectWrapper newClientSettings;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {new ClientSettingsObjectWrapper(getDefaultClientSettings())},
                {new ClientSettingsObjectWrapper(getClientSettingsTypeWithoutSubscriptionEmailsAndUnchecked())},
                {new ClientSettingsObjectWrapper(getClientSettingsTypeWithSubscriptionEmails())},
                {new ClientSettingsObjectWrapper(getClientSettingsTypeWithSubscriptionEmailsAndUnchecked())}

        });
    }

    @Before
    public void setup() {
        user = new UserSteps().withUser(USER);
        superUser = new UserSteps().withUser(SUPER_USER);

        returnedClientSettings = superUser.onInternalSteps().onClientSettingsSteps().
                rewriteClientSettingsAndExpectSuccess(newClientSettings, USER.get(User.UID));
    }

    @Test
    public void checkAddedClientSettings() {
        assertThat("перезаписанные настройки рассылки должны быть эквивалентны ожидаемым", returnedClientSettings,
                beanEquivalent(newClientSettings.get()));
    }

    @Test
    public void checkClientSettings() {
        returnedClientSettings = user.onManagementSteps().onClientSettingsSteps().getClientSettingsAndExpectSuccess();
        assertThat("возвращаемые настройки рассылки должны быть эквивалентны ожидаемым", returnedClientSettings,
                beanEquivalent(newClientSettings.get()));
    }


}
