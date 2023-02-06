package ru.yandex.autotests.metrika.tests.ft.management.notifications;

import java.util.List;
import java.util.stream.Collectors;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.data.parameters.CommonParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.notification.ExternalNotification;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static com.google.common.collect.ImmutableList.of;
import static org.hamcrest.CoreMatchers.not;
import static org.hamcrest.core.IsCollectionContaining.hasItem;
import static ru.yandex.autotests.metrika.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getNotificationWithUIDs;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

/**
 * Created by sourx on 26.07.16.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.NOTIFICATIONS)
@Title("Уведомление: отсутствие доступа к чужим уведомлениям")
public class NotificationsUidNegativeTest {
    private final static User SIMPLE = Users.SIMPLE_USER;
    private final static User OTHER_USER = Users.SIMPLE_USER2;
    private final static User SUPER = Users.SUPER_USER;

    private UserSteps superUser;
    private UserSteps user;
    private Long notificationId;

    @Before
    public void setup() {
        superUser = new UserSteps().withUser(SUPER);
        user = new UserSteps().withUser(SIMPLE);

        notificationId = superUser.onInternalSteps().onNotificationSteps()
                .addNotificationAndExpectSuccess(getNotificationWithUIDs(of(OTHER_USER.get(User.UID)))).getId();

        List<Long> notificationIds = user.onManagementSteps().onNotificationsSteps()
                .getNotificationAndExpectSuccess(new CommonParameters().withLang("ru")).stream()
                .map(ExternalNotification::getId)
                .collect(Collectors.toList());

        assumeThat("уведомление отсутствует в списке", notificationIds, not(hasItem(notificationId)));
    }

    @Test
    @Title("Нельзя закрыть чужое уведомление")
    public void tryToAccess() {
        user.onManagementSteps().onNotificationsSteps().deleteNotificationAndExpectError(ACCESS_DENIED, notificationId);
    }

    @After
    public void teardown() {
        superUser.onInternalSteps().onNotificationSteps().deleteNotificationAndExpectSuccess(notificationId);
    }
}
