package ru.yandex.autotests.metrika.tests.ft.internal;

import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.errors.CommonError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

@Features(Requirements.Feature.WEB_SERVER_SETTINGS)
@Stories(Requirements.Story.Internal.WEB_SERVER_SETTINGS)
@Title("Проверка запроса с пустым телом")
public class EmptyBodyTest {

    private static UserSteps userSteps;

    @BeforeClass
    public static void init() {
        userSteps = new UserSteps().withUser(Users.SIMPLE_USER).useTesting();
    }

    @Test
    public void testEmptyBody() {
        userSteps.onManagementSteps().onCountersSteps().tryCreateCounterWithEmptyBody(CommonError.REQUEST_BODY_IS_MISSING);
    }
}
