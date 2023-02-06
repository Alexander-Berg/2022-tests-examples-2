package ru.yandex.autotests.metrika.tests.ft.management.notifications;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.NotificationObjectWrapper;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.data.parameters.CommonParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.notification.ExternalNotification;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;
import java.util.stream.Collectors;

import static com.google.common.collect.ImmutableList.of;
import static java.util.Arrays.asList;
import static org.hamcrest.CoreMatchers.not;
import static org.hamcrest.core.IsCollectionContaining.hasItem;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.*;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.createNotificationParam;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by sourx on 26.07.16.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.NOTIFICATIONS)
@Title("Уведомление: просмотр уведомлений пользователем (негативные)")
@RunWith(Parameterized.class)
public class NotificationsNegativeTest {
    private final static User SIMPLE = Users.SIMPLE_USER;

    private UserSteps superUser;
    private UserSteps user;
    private Long notificationId;

    @Parameterized.Parameter()
    public NotificationObjectWrapper notification;

    @Parameterized.Parameter(1)
    public String lang;

    @Parameterized.Parameters(name = "Уведомление: {0}, язык: {1}")
    public static List<Object> createParameters() {
        return asList(
                createNotificationParam(getDefaultNotification(), "en"),
                createNotificationParam(getDefaultNotification(), "tr"),
                createNotificationParam(getNotificationWithOnlyEnTitle(), "ru"),
                createNotificationParam(getNotificationWithUIDs(of(Users.SIMPLE_USER2.get(User.UID))), "ru")
        );
    }

    @Before
    public void setup() {
        superUser = new UserSteps().withUser(Users.SUPER_USER);
        user = new UserSteps().withUser(SIMPLE);

        notificationId = superUser.onInternalSteps().onNotificationSteps()
                .addNotificationAndExpectSuccess(notification.get()).getId();
    }

    @Test
    public void checkNotification() {
        List<Long> notificationIds = user.onManagementSteps().onNotificationsSteps()
                .getNotificationAndExpectSuccess(new CommonParameters().withLang(lang)).stream()
                .map(ExternalNotification::getId)
                .collect(Collectors.toList());

        assertThat("уведомление отсутствует в списке", notificationIds, not(hasItem(notificationId)));
    }

    @After
    public void teardown() {
        superUser.onInternalSteps().onNotificationSteps().deleteNotificationAndExpectSuccess(notificationId);
    }
}
