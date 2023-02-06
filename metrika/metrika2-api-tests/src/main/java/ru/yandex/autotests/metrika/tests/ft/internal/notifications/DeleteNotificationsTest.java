package ru.yandex.autotests.metrika.tests.ft.internal.notifications;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.notification.Notification;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getDefaultNotification;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by sourx on 25.07.16.
 */
@Features(Requirements.Feature.INTERNAL)
@Stories(Requirements.Story.Internal.NOTIFICATIONS)
@Title("Уведомление: удаление")
@RunWith(Parameterized.class)
public class DeleteNotificationsTest {
    private final static User SUPPORT = Users.SUPPORT;
    private final static User SUPER = Users.SUPER_USER;

    private UserSteps user;
    private Long notificationId;

    @Parameterized.Parameter()
    public String title;

    @Parameterized.Parameter(1)
    public User userParam;

    @Parameterized.Parameters(name = "Пользователь: {0}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {"саппорт", SUPPORT},
                {"супер", SUPER}
        });
    }

    @Before
    public void setup() {
        user = new UserSteps().withUser(userParam);

        notificationId = user.onInternalSteps().onNotificationSteps()
                .addNotificationAndExpectSuccess(getDefaultNotification()).getId();
    }

    @Test
    public void deleteNotification() {
        user.onInternalSteps().onNotificationSteps().deleteNotificationAndExpectSuccess(notificationId);

        List<Notification> availableNotifications = user.onInternalSteps().onNotificationSteps().getNotifications();
        List<Long> availableNotificationsId = availableNotifications.stream().map(Notification::getId).collect(Collectors.toList());

        assertThat("удаленное уведомление отсутствует в списке",
                availableNotificationsId, not(hasItem(notificationId)));
    }
}
