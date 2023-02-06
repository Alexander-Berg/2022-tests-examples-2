package ru.yandex.autotests.metrika.tests.ft.management.client_settings.permission;

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

import static ru.yandex.autotests.metrika.data.parameters.StaticParameters.uid;
import static ru.yandex.autotests.metrika.errors.ManagementError.ACCESS_DENIED;

/**
 * Created by omatikaya on 22.02.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.CLIENT_SETTINGS)
@Title("Проверка прав изменения настроек новостной рассылки")
public class EditClientSettingsPermissionTest {
    private final static User USER_OWNER = Users.USER_FOR_EMAIL_SUBSCRIPTION3;
    private final static User USER_WITHOUT_WRITE_RIGHTS = Users.SIMPLE_USER2;
    private final static User USER_WITH_WRITE_RIGHTS = Users.SUPER_USER;
    private final static User SUPER_USER = Users.SUPER_USER;

    private UserSteps userOwner;
    private UserSteps userWithoutWriteRights;
    private UserSteps userWithWriteRights;
    private UserSteps superUser;

    private ClientSettingsObjectWrapper clientSettings;
    private ClientSettings currentClientSettings;

    @Before
    public void setup() {
        userOwner = new UserSteps().withUser(USER_OWNER);
        userWithoutWriteRights = new UserSteps().withUser(USER_WITHOUT_WRITE_RIGHTS);
        userWithWriteRights = new UserSteps().withUser(USER_WITH_WRITE_RIGHTS);
        superUser = new UserSteps().withUser(SUPER_USER);

        clientSettings = new ClientSettingsObjectWrapper(ManagementTestData.getDefaultClientSettings());
        currentClientSettings = userOwner.onManagementSteps().onClientSettingsSteps().getClientSettingsAndExpectSuccess();
    }

    @Test
    public void userOwnerAccessTest() {
        userOwner.onManagementSteps().onClientSettingsSteps().saveClientSettingsAndExpectSuccess(clientSettings);
    }

    @Test
    public void userWithoutWriteRightsNoAccessTest() {
        userWithoutWriteRights.onManagementSteps().onClientSettingsSteps().saveClientSettingsAndExpectError(
                ACCESS_DENIED,
                clientSettings,
                uid(USER_OWNER.get(User.UID))
        );
    }

    @Test
    public void userWithWriteRightsAccessTest() {
        userWithWriteRights.onManagementSteps().onClientSettingsSteps().saveClientSettingsAndExpectSuccess(
                clientSettings,
                uid(USER_OWNER.get(User.UID))
        );
    }
}
