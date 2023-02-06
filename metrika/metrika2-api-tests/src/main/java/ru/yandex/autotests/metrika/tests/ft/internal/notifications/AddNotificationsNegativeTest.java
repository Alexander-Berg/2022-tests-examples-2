package ru.yandex.autotests.metrika.tests.ft.internal.notifications;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.NotificationObjectWrapper;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.errors.CommonError.MAY_NOT_BE_NULL;
import static ru.yandex.autotests.metrika.errors.InternalError.*;
import static ru.yandex.autotests.metrika.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.*;

/**
 * Created by sourx on 21.07.16.
 */
@Features(Requirements.Feature.INTERNAL)
@Stories(Requirements.Story.Internal.NOTIFICATIONS)
@Title("Уведомление: добавление (негативные)")
@RunWith(Parameterized.class)
public class AddNotificationsNegativeTest {
    private final static User SIMPLE = Users.SIMPLE_USER;
    private final static User MANAGER = Users.MANAGER;
    private final static User MANAGER_DIRECT = Users.MANAGER_DIRECT;
    private final static User UNAUTHORIZED = Users.USER_WITH_EMPTY_TOKEN;

    private UserSteps user;

    @Parameterized.Parameter()
    public User userParam;

    @Parameterized.Parameter(1)
    public NotificationObjectWrapper notification;

    @Parameterized.Parameter(2)
    public IExpectedError error;

    @Parameterized.Parameters(name = "Уведомление: {1}, ошибка: {2}")
    public static List<Object> createParameters() {
        return asList(
                createNotificationNegativeParam(getNotificationWithoutDate(), MAY_NOT_BE_NULL),
                createNotificationNegativeParam(getNotificationWithMoreThanMaxTitle(), TOO_LONG_TITLE),
                createNotificationNegativeParam(getNotificationWithMoreThanMaxBody(), TOO_LONG_BODY),
                createNotificationNegativeParam(getNotificationWithoutContent(), TITLE_SIZE_MUST_BE_MORE_NULL),
                createNotificationNegativeParam(getNotificationWithEmptyStringInDate(), INVALID_START_DATE_FORMAT),
                createNotificationNegativeParam(SIMPLE, getDefaultNotification(), ACCESS_DENIED),
                createNotificationNegativeParam(MANAGER, getDefaultNotification(), ACCESS_DENIED),
                createNotificationNegativeParam(MANAGER_DIRECT, getDefaultNotification(), ACCESS_DENIED),
                createNotificationNegativeParam(UNAUTHORIZED, getDefaultNotification(), ACCESS_DENIED)
        );
    }

    @Before
    public void setup() {
        user = new UserSteps().withUser(userParam);
    }

    @Test
    public void checkTryAdd() {
        user.onInternalSteps().onNotificationSteps()
                .addNotificationAndExpectError(error, notification.get());
    }
}
