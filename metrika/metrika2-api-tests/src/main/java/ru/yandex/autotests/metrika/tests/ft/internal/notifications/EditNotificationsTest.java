package ru.yandex.autotests.metrika.tests.ft.internal.notifications;

import java.util.List;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.NotificationObjectWrapper;
import ru.yandex.autotests.metrika.data.common.actions.EditAction;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.notification.Notification;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.createNotificationEditParam;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getChangeCloseAfterFollow;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getChangeContent;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getChangeContentWithMaxBody;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getChangeContentWithMaxTitle;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getChangeEndDate;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getChangeLocation;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getChangeObjIds;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getChangePending;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getChangeScope;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getChangeStartDate;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getChangeType;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getChangeUIDs;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getChangeVisitParam;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getDefaultNotification;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getNotificationVisitParam;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getNotificationWithScope;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.metrika.api.management.client.notification.ExternalNotificationInnerLocation.BANNER;
import static ru.yandex.metrika.api.management.client.notification.ExternalNotificationInnerLocation.BELL;
import static ru.yandex.metrika.api.management.client.notification.ExternalNotificationInnerType.CRITICAL;
import static ru.yandex.metrika.api.management.client.notification.ExternalNotificationInnerType.UPDATE;

/**
 * Created by sourx on 22.07.16.
 */
@Features(Requirements.Feature.INTERNAL)
@Stories(Requirements.Story.Internal.NOTIFICATIONS)
@Title("Уведомление: редактирование")
@RunWith(Parameterized.class)
public class EditNotificationsTest {

    private UserSteps user;

    private Long notificationId;
    private Notification changedNotification;
    private Notification editedNotification;

    @Parameterized.Parameter()
    public User userParam;

    @Parameterized.Parameter(1)
    public NotificationObjectWrapper notification;

    @Parameterized.Parameter(2)
    public EditAction<Notification> notificationChangeAction;

    @Parameterized.Parameters(name = "{2}")
    public static List<Object> createParameters() {
        return asList(
                createNotificationEditParam(getDefaultNotification(), getChangeContent()),
                createNotificationEditParam(getDefaultNotification(), getChangeType(UPDATE)),
                createNotificationEditParam(getDefaultNotification(), getChangeType(CRITICAL)),
                createNotificationEditParam(getDefaultNotification(), getChangeLocation(BELL)),
                createNotificationEditParam(getDefaultNotification(), getChangeLocation(BANNER)),
                createNotificationEditParam(getDefaultNotification(), getChangeVisitParam(getNotificationVisitParam())),
                createNotificationEditParam(getDefaultNotification(), getChangeStartDate()),
                createNotificationEditParam(getDefaultNotification(), getChangeEndDate()),
                createNotificationEditParam(getDefaultNotification(), getChangeCloseAfterFollow(true)),
                createNotificationEditParam(getDefaultNotification(), getChangePending(false)),
                createNotificationEditParam(getDefaultNotification(), getChangeContentWithMaxTitle()),
                createNotificationEditParam(getDefaultNotification(), getChangeContentWithMaxBody()),
                createNotificationEditParam(getDefaultNotification(), getChangeScope()),
                createNotificationEditParam(getNotificationWithScope(), getChangeScope()),
                createNotificationEditParam(getDefaultNotification(), getChangeUIDs(asList(123L, 456L))),
                createNotificationEditParam(getDefaultNotification(), getChangeObjIds(asList(123L, 456L))),
                createNotificationEditParam(Users.SUPER_USER, getDefaultNotification(), getChangeContent())
        );
    }

    @Before
    public void setup() {
        user = new UserSteps().withUser(userParam);

        notificationId = user.onInternalSteps().onNotificationSteps()
                .addNotificationAndExpectSuccess(notification.get()).getId();
        changedNotification = notificationChangeAction.edit(notification.get());
        editedNotification = user.onInternalSteps().onNotificationSteps()
                .editNotificationAndExpectSuccess(notificationId, changedNotification);
    }

    @Test
    public void checkEdited() {
        assertThat("отредактированное уведомление эквивалентно измененному уведомлению",
                editedNotification, beanEquivalent(changedNotification));
    }

    @Test
    public void checkInfo() {
        Notification notificationInfo = user.onInternalSteps().onNotificationSteps()
                .getNotificationAndExpextSuccess(notificationId);

        assertThat("информация об отредактированном уведомлении эквивалентна измененному уведомлению",
                notificationInfo, beanEquivalent(changedNotification));
    }

    @After
    public void teardown() {
        user.onInternalSteps().onNotificationSteps().deleteNotificationAndExpectSuccess(notificationId);
    }
}
