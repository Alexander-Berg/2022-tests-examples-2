package ru.yandex.autotests.metrika.tests.ft.internal.notifications;

import java.util.List;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.NotificationObjectWrapper;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.notification.Notification;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.createNotificationParam;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getCriticalNotification;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getDefaultNotification;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getNotificationVisitParam;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getNotificationWithCloseAfterFollow;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getNotificationWithFullContent;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getNotificationWithIcon;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getNotificationWithLocation;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getNotificationWithMaxBody;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getNotificationWithMaxTitle;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getNotificationWithObjIds;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getNotificationWithOnlyEnTitle;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getNotificationWithOnlyTrTitle;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getNotificationWithOnlyUaTitle;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getNotificationWithPending;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getNotificationWithUIDs;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getNotificationWithVisitParam;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getUpdateNotification;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.metrika.api.management.client.notification.ExternalNotificationInnerLocation.BANNER;
import static ru.yandex.metrika.api.management.client.notification.ExternalNotificationInnerLocation.BELL;
import static ru.yandex.metrika.api.management.client.notification.ExternalNotificationInnerLocation.ROW;

/**
 * Created by sourx on 21.07.16.
 */
@Features(Requirements.Feature.INTERNAL)
@Stories(Requirements.Story.Internal.NOTIFICATIONS)
@Title("Уведомление: добавление")
@RunWith(Parameterized.class)
public class AddNotificationsTest {
    private UserSteps user;

    private Notification addedNotification;
    private Long notificationId;

    @Parameterized.Parameter()
    public User userParam;

    @Parameterized.Parameter(1)
    public NotificationObjectWrapper expectedNotification;

    @Parameterized.Parameters(name = "Уведомление: {1}")
    public static List<Object> createParameters() {
        return asList(
                createNotificationParam(getDefaultNotification()),
                createNotificationParam(getNotificationWithOnlyEnTitle()),
                createNotificationParam(getNotificationWithOnlyUaTitle()),
                createNotificationParam(getNotificationWithOnlyTrTitle()),
                createNotificationParam(getNotificationWithFullContent()),
                createNotificationParam(getUpdateNotification()),
                createNotificationParam(getCriticalNotification()),
                createNotificationParam(getNotificationWithLocation(ROW)),
                createNotificationParam(getNotificationWithLocation(BELL)),
                createNotificationParam(getNotificationWithLocation(BANNER)),
                createNotificationParam(getNotificationWithVisitParam(getNotificationVisitParam())),
                createNotificationParam(getNotificationWithCloseAfterFollow(true)),
                createNotificationParam(getNotificationWithPending(true)),
                createNotificationParam(getNotificationWithMaxTitle()),
                createNotificationParam(getNotificationWithMaxBody()),
                createNotificationParam(getNotificationWithIcon()),
                createNotificationParam(getNotificationWithUIDs(asList(123L, 456L))),
                createNotificationParam(getNotificationWithObjIds(asList(123L, 456L))),
                createNotificationParam(Users.SUPER_USER, getDefaultNotification())
        );
    }

    @Before
    public void setup() {
        user = new UserSteps().withUser(userParam);

        addedNotification = user.onInternalSteps().onNotificationSteps()
                .addNotificationAndExpectSuccess(expectedNotification.get());
        notificationId = addedNotification.getId();
    }

    @Test
    public void checkAdded() {
        assertThat("добавленное уведомление должно быть эквивалентно добавляемому", addedNotification,
                beanEquivalent(expectedNotification.get()));
    }

    @Test
    public void checkInfo() {
        Notification actualNotification = user.onInternalSteps().onNotificationSteps()
                .getNotificationAndExpextSuccess(notificationId);

        assertThat("информация об уведомлении должна быть эквивалента добавленному уведомлению", actualNotification,
                beanEquivalent(expectedNotification.get()));
    }

    @After
    public void teardown() {
        user.onInternalSteps().onNotificationSteps().deleteNotificationAndExpectSuccess(notificationId);
    }
}
