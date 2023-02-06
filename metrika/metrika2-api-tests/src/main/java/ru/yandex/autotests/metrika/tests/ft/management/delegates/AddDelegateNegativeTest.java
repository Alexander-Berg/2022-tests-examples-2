package ru.yandex.autotests.metrika.tests.ft.management.delegates;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.errors.ManagementError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.DelegateE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Arrays;

import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_WITH_INVALID_LOGIN;
import static ru.yandex.autotests.metrika.errors.ManagementError.*;

/**
 * Created by hamilkar on 10/24/16.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.DELEGATE)
@Title("Добавление представителя (негативные)")
public class AddDelegateNegativeTest {
    private final User OWNER = Users.USER_DELEGATOR2;

    private UserSteps userSteps;

    @Before
    public void setup() {
        userSteps = new UserSteps().withUser(OWNER);
    }

    @Test
    public void invalidLoginTestEN() {
        userSteps.withLang("en").onManagementSteps().onDelegatesSteps().addDelegateAndExpectError(
                USER_NOT_FOUND_EN,
                new DelegateE().withUserLogin(USER_WITH_INVALID_LOGIN.get(LOGIN)).withComment("Test comment")
        );
    }

    @Test
    public void invalidLoginTestRU() {
        userSteps.withLang("ru").onManagementSteps().onDelegatesSteps().addDelegateAndExpectError(
                USER_NOT_FOUND_RU,
                new DelegateE().withUserLogin(USER_WITH_INVALID_LOGIN.get(LOGIN)).withComment("Test comment")
        );
    }

    @Test
    public void commentWithNotAllowedSymbols() {
        userSteps.withLang("ru").onManagementSteps().onDelegatesSteps().addDelegateAndExpectError(
                NOT_ALLOWED_SYMBOLS_IN_COMMENT,
                new DelegateE().withUserLogin(SIMPLE_USER.get(LOGIN)).withComment("\uD83D\uDCC5")
        );
    }
}
