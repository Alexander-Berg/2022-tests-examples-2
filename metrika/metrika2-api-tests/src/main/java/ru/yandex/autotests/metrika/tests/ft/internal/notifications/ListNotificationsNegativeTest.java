package ru.yandex.autotests.metrika.tests.ft.internal.notifications;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getDefaultNotification;

/**
 * Created by sourx on 25.07.16.
 */
@Features(Requirements.Feature.INTERNAL)
@Stories(Requirements.Story.Internal.NOTIFICATIONS)
@Title("Проверка получения списка уведомлений (негативные)")
@RunWith(Parameterized.class)
public class ListNotificationsNegativeTest {
    private final static User SIMPLE = Users.SIMPLE_USER;
    private final static User MANAGER = Users.MANAGER;
    private final static User MANAGER_DIRECT = Users.MANAGER_DIRECT;
    private final static User UNAUTHORIZED = Users.USER_WITH_EMPTY_TOKEN;

    private UserSteps superUser;
    private UserSteps user;
    private Long notificationId;

    @Parameterized.Parameter()
    public String title;

    @Parameterized.Parameter(1)
    public User userParam;

    @Parameterized.Parameters(name = "Пользователь: {0}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {"обычный", SIMPLE},
                {"менеджер", MANAGER},
                {"менеджер-директ", MANAGER_DIRECT},
                {"неавторизованный", UNAUTHORIZED}
        });
    }

    @Before
    public void setup() {
        superUser = new UserSteps().withUser(Users.SUPER_USER);
        user = new UserSteps().withUser(userParam);

        notificationId = superUser.onInternalSteps().onNotificationSteps()
                .addNotificationAndExpectSuccess(getDefaultNotification()).getId();
    }

    @Test
    public void tryGetNotification() {
        user.onInternalSteps().onNotificationSteps().getNotificationsAndExpectError(ACCESS_DENIED);
    }

    @After
    public void teardown() {
        superUser.onInternalSteps().onNotificationSteps().deleteNotificationAndExpectSuccess(notificationId);
    }
}
