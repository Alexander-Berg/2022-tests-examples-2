package ru.yandex.autotests.metrika.tests.ft.management.client_settings.permission;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
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
@Title("Проверка прав получения настроек новостной рассылки")
public class GetClientSettingsPermissionTest {
    private final static User USER_OWNER = Users.USER_FOR_EMAIL_SUBSCRIPTION1;
    private final static User USER_WITHOUT_READ_RIGHTS = Users.SIMPLE_USER2;
    private final static User USER_WITH_READ_RIGHTS = Users.MANAGER;

    private UserSteps userOwner;
    private UserSteps userWithoutReadRights;
    private UserSteps userWithReadRights;

    @Before
    public void setup() {
        userOwner = new UserSteps().withUser(USER_OWNER);
        userWithoutReadRights = new UserSteps().withUser(USER_WITHOUT_READ_RIGHTS);
        userWithReadRights = new UserSteps().withUser(USER_WITH_READ_RIGHTS);
    }

    @Test
    public void userOwnerAccessTest() {
        userOwner.onManagementSteps().onClientSettingsSteps().getClientSettingsAndExpectSuccess();
    }

    @Test
    public void userWithoutReadRightsNoAccessTest() {
        userWithoutReadRights.onManagementSteps().onClientSettingsSteps().getClientSettingsAndExpectError(
                ACCESS_DENIED,
                uid(USER_OWNER.get(User.UID))
        );
    }

    @Test
    public void userWithReadRightsAccessTest() {
        userWithReadRights.onManagementSteps().onClientSettingsSteps().getClientSettingsAndExpectSuccess(
                uid(USER_OWNER.get(User.UID))
        );
    }
}
