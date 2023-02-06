package ru.yandex.autotests.metrika.tests.ft.management.notifications;

import java.util.List;
import java.util.stream.Collectors;

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

import static java.util.Arrays.asList;
import static org.hamcrest.CoreMatchers.not;
import static org.hamcrest.core.IsCollectionContaining.hasItem;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getDefaultNotification;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getNotificationWithFullContent;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getNotificationWithOnlyEnTitle;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getNotificationWithOnlyTrTitle;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getNotificationWithUIDs;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.createNotificationParam;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

/**
 * Created by sourx on 20.07.16.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.NOTIFICATIONS)
@Title("Уведомление: просмотр уведомлений пользователем")
@RunWith(Parameterized.class)
public class NotificationsTest {
    private final static User SIMPLE = Users.SIMPLE_USER;
    private final static User SUPER = Users.SUPER_USER;

    private UserSteps superUser;
    private UserSteps user;
    private Long notificationId;

    private List<Long> notificationsId;

    @Parameterized.Parameter()
    public NotificationObjectWrapper notification;

    @Parameterized.Parameter(1)
    public String lang;

    @Parameterized.Parameters(name = "Уведомление: {0}, язык: {1}")
    public static List<Object> createParameters() {
        return asList(
                createNotificationParam(getDefaultNotification(), "ru"),
                createNotificationParam(getNotificationWithUIDs(asList(SIMPLE.get(User.UID), 123L)), "ru"),
                createNotificationParam(getNotificationWithOnlyEnTitle(), "en"),
                createNotificationParam(getNotificationWithOnlyTrTitle(), "tr"),
                createNotificationParam(getNotificationWithFullContent(), "ru"),
                createNotificationParam(getNotificationWithFullContent(), "en"),
                createNotificationParam(getNotificationWithFullContent(), "tr")
        );
    }

    @Before
    public void setup() {
        superUser = new UserSteps().withUser(SUPER);
        user = new UserSteps().withUser(SIMPLE);

        notificationId = superUser.onInternalSteps().onNotificationSteps()
                .addNotificationAndExpectSuccess(notification.get()).getId();

        notificationsId = user.onManagementSteps().onNotificationsSteps()
                .getNotificationAndExpectSuccess(new CommonParameters().withLang(lang)).stream()
                .map(ExternalNotification::getId)
                .collect(Collectors.toList());

        assumeThat("уведомление присутствует в списке", notificationsId, hasItem(notificationId));
    }

    @Test
    public void checkNotification() {
        user.onManagementSteps().onNotificationsSteps().deleteNotificationAndExpectSuccess(notificationId);

        notificationsId = user.onManagementSteps().onNotificationsSteps()
                .getNotificationAndExpectSuccess(new CommonParameters().withLang(lang)).stream()
                .map(ExternalNotification::getId)
                .collect(Collectors.toList());

        assertThat("уведомление отсутствует в списке", notificationsId, not(hasItem(notificationId)));
    }

    @After
    public void teardown() {
        superUser.onInternalSteps().onNotificationSteps().deleteNotificationAndExpectSuccess(notificationId);
    }
}
