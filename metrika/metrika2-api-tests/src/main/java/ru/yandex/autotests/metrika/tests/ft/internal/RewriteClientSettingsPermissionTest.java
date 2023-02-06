package ru.yandex.autotests.metrika.tests.ft.internal;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.ClientSettingsObjectWrapper;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData;
import ru.yandex.metrika.api.management.client.ClientSettings;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.errors.ManagementError.ACCESS_DENIED;

/**
 * Created by omatikaya on 22.02.17.
 */
@Features(Requirements.Feature.INTERNAL)
@Stories(Requirements.Story.Internal.CLIENT_SETTINGS)
@Title("Проверка прав перезаписи настроек новостной рассылки")
public class RewriteClientSettingsPermissionTest {
    private final static User TARGET_USER = Users.USER_FOR_EMAIL_SUBSCRIPTION4;
    private final static User USER_WITHOUT_REWRITE_RIGHTS = Users.SIMPLE_USER;
    private final static User USER_WITH_REWRITE_RIGHTS = Users.SUPER_USER;

    private UserSteps targetUser;
    private UserSteps userWithoutRewriteRights;
    private UserSteps userWithRewriteRights;

    private ClientSettingsObjectWrapper clientSettings;
    private ClientSettings currentClientSettings;

    @Before
    public void setup() {
        targetUser = new UserSteps().withUser(TARGET_USER);
        userWithoutRewriteRights = new UserSteps().withUser(USER_WITHOUT_REWRITE_RIGHTS);
        userWithRewriteRights = new UserSteps().withUser(USER_WITH_REWRITE_RIGHTS);

        clientSettings = new ClientSettingsObjectWrapper(ManagementTestData.getDefaultClientSettings());
        currentClientSettings = targetUser.onManagementSteps().onClientSettingsSteps().getClientSettingsAndExpectSuccess();
    }

    @Test
    public void userWithoutRewriteRightsNoAccessTest() {
        userWithoutRewriteRights.onInternalSteps().onClientSettingsSteps().rewriteClientSettingsAndExpectError(
                ACCESS_DENIED,
                clientSettings,
                TARGET_USER.get(User.UID)
        );
    }

    @Test
    public void userWithRewriteRightsAccessTest() {
        userWithRewriteRights.onInternalSteps().onClientSettingsSteps().rewriteClientSettingsAndExpectSuccess(
                clientSettings,
                TARGET_USER.get(User.UID)
        );
    }
}
