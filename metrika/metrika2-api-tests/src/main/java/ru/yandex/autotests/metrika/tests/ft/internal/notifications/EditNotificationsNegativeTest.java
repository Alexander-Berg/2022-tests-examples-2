package ru.yandex.autotests.metrika.tests.ft.internal.notifications;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.NotificationObjectWrapper;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.common.actions.EditAction;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.notification.Notification;
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
 * Created by sourx on 22.07.16.
 */
@Features(Requirements.Feature.INTERNAL)
@Stories(Requirements.Story.Internal.NOTIFICATIONS)
@Title("Уведомление: редактирование (негативные)")
@RunWith(Parameterized.class)
public class EditNotificationsNegativeTest {
    private final static User SIMPLE = Users.SIMPLE_USER;
    private final static User MANAGER = Users.MANAGER;
    private final static User MANAGER_DIRECT = Users.MANAGER_DIRECT;
    private final static User UNAUTHORIZED = Users.USER_WITH_EMPTY_TOKEN;

    private UserSteps superUser;
    private UserSteps user;

    private Long notificationId;
    private Notification changedNotification;

    @Parameterized.Parameter()
    public User userParam;

    @Parameterized.Parameter(1)
    public NotificationObjectWrapper notification;

    @Parameterized.Parameter(2)
    public EditAction<Notification> notificationChangeAction;

    @Parameterized.Parameter(3)
    public IExpectedError error;

    @Parameterized.Parameters(name = "{2}; {3}")
    public static List<Object> createParameters() {
        return asList(
                createNotificationNegativeEditParam(getDefaultNotification(), getChangeEmptyTitle(),
                        TITLE_SIZE_MUST_BE_MORE_NULL),
                createNotificationNegativeEditParam(getDefaultNotification(), getChangeContentWithMoreThanMaxTitle(),
                        TOO_LONG_TITLE),
                createNotificationNegativeEditParam(getDefaultNotification(), getChangeContentWithMoreThanMaxBody(),
                        TOO_LONG_BODY),
                createNotificationNegativeEditParam(getDefaultNotification(), getChangeDateToEmptyString(),
                        INVALID_START_DATE_FORMAT),
                createNotificationNegativeEditParam(getDefaultNotification(), getChangeDateToNull(),
                        MAY_NOT_BE_NULL),
                createNotificationNegativeEditParam(SIMPLE, getDefaultNotification(), getChangeContent(),
                        ACCESS_DENIED),
                createNotificationNegativeEditParam(MANAGER, getDefaultNotification(), getChangeContent(),
                        ACCESS_DENIED),
                createNotificationNegativeEditParam(MANAGER_DIRECT, getDefaultNotification(), getChangeContent(),
                        ACCESS_DENIED),
                createNotificationNegativeEditParam(UNAUTHORIZED, getDefaultNotification(), getChangeContent(),
                        ACCESS_DENIED)
        );
    }

    @Before
    public void setup() {
        superUser = new UserSteps().withUser(Users.SUPER_USER);
        user = new UserSteps().withUser(userParam);

        notificationId = superUser.onInternalSteps().onNotificationSteps()
                .addNotificationAndExpectSuccess(notification.get()).getId();
        changedNotification = notificationChangeAction.edit(notification.get());
    }

    @Test
    public void checkTryEdit() {
        user.onInternalSteps().onNotificationSteps()
                .editNotificationAndExpectError(error, notificationId, changedNotification);
    }

    @After
    public void teardown() {
        superUser.onInternalSteps().onNotificationSteps().deleteNotificationAndExpectSuccess(notificationId);
    }
}
