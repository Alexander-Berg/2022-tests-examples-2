package ru.yandex.autotests.metrika.tests.ft.internal;

import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features(Requirements.Feature.WEB_SERVER_SETTINGS)
@Stories(Requirements.Story.Internal.WEB_SERVER_SETTINGS)
@Title("Запрос JSP страницы")
public class NoSenseJspTest {
    private static UserSteps userSteps;

    @BeforeClass
    public static void init() {
        userSteps = new UserSteps().withUser(Users.SIMPLE_USER).useTesting();
    }

    @Test
    public void jspRequest404Result() {
        int serverResponseStatus = userSteps.onJspRequestSteps().getServerResponseStatus();
        assertThat("запрос jsp страницы возвращает 404", serverResponseStatus, equalTo(404));
    }
}
