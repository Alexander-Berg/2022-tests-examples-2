package ru.yandex.autotests.metrika.tests.ft.management.notifications;

import java.util.List;
import java.util.stream.Collectors;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.data.parameters.CommonParameters;
import ru.yandex.autotests.metrika.data.parameters.management.v1.NotificationsParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.notification.ExternalNotification;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.CoreMatchers.not;
import static org.hamcrest.core.IsCollectionContaining.hasItem;
import static ru.yandex.autotests.metrika.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.metrika.tests.ft.internal.InternalTestData.getNotificationWithObjIds;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getCounterWithBasicParameters;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getGrant;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.NOTIFICATIONS)
@Title("Уведомление: просмотр уведомлений счётчика пользователем")
public class NotificationsObjIdsTest {

    private static final User SIMPLE = Users.SIMPLE_USER;
    private static final User OTHER_USER = Users.SIMPLE_USER2;
    private static final User SUPER = Users.SUPER_USER;

    private UserSteps superUser;
    private UserSteps user;
    private UserSteps otherUser;
    private Long notificationId;
    private Long counterId;
    private Long counterId2;

    private List<Long> notificationsId;

    @Before
    public void setup() {
        superUser = new UserSteps().withUser(SUPER);
        user = new UserSteps().withUser(SIMPLE);
        otherUser = new UserSteps().withUser(OTHER_USER);

        counterId = otherUser.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getCounterWithBasicParameters())
                .getId();

        notificationId = superUser.onInternalSteps().onNotificationSteps()
                .addNotificationAndExpectSuccess(getNotificationWithObjIds(ImmutableList.of(counterId)))
                .getId();
    }

    @Test
    @Title("Можно прочитать уведомление счетчика при наличии доступа на счетчик")
    public void testAccess() {
        superUser.onManagementSteps().onGrantsSteps().setGrantAndExpectSuccess(counterId, getGrant(SIMPLE));

        notificationsId = user.onManagementSteps().onNotificationsSteps()
                .getNotificationAndExpectSuccess(new CommonParameters().withLang("ru")).stream()
                .map(ExternalNotification::getId)
                .collect(Collectors.toList());

        assertThat("уведомление присутствует в списке", notificationsId, hasItem(notificationId));
    }

    @Test
    @Title("Нельзя прочитать уведомление счетчика без доступа на счетчик")
    public void testNoAccess() {
        notificationsId = user.onManagementSteps().onNotificationsSteps()
                .getNotificationAndExpectSuccess(new CommonParameters().withLang("ru")).stream()
                .map(ExternalNotification::getId)
                .collect(Collectors.toList());

        assertThat("уведомление отсутствует в списке", notificationsId, not(hasItem(notificationId)));
    }

    @Test
    @Title("Можно закрыть уведомление счетчика при наличии доступа на счетчик")
    public void testAccessForMarking() {
        superUser.onManagementSteps().onGrantsSteps().setGrantAndExpectSuccess(counterId, getGrant(SIMPLE));
        user.onManagementSteps().onNotificationsSteps().deleteNotificationAndExpectSuccess(notificationId);
    }

    @Test
    @Title("Нельзя закрыть уведомление счетчика без доступа на счетчик")
    public void testNoAccessForMarking() {
        user.onManagementSteps().onNotificationsSteps().deleteNotificationAndExpectError(ACCESS_DENIED, notificationId);
    }

    @Test
    @Title("Уведомление доступно менеджеру")
    public void testManagerAccess() {
        notificationsId = superUser.onManagementSteps().onNotificationsSteps()
                .getNotificationAndExpectSuccess(new CommonParameters().withLang("ru")).stream()
                .map(ExternalNotification::getId)
                .collect(Collectors.toList());

        assertThat("уведомление присутствует в списке", notificationsId, hasItem(notificationId));
    }

    @Test
    @Title("Уведомление видно со страницы счетчика")
    public void testObjIdFilterNonEmptyResult() {
        superUser.onManagementSteps().onGrantsSteps().setGrantAndExpectSuccess(counterId, getGrant(SIMPLE));

        notificationsId = user.onManagementSteps().onNotificationsSteps()
                .getNotificationAndExpectSuccess(new NotificationsParameters()
                        .withLang("ru")
                        .withObjId(counterId))
                .stream()
                .map(ExternalNotification::getId)
                .collect(Collectors.toList());

        assertThat("уведомление присутствует в списке", notificationsId, hasItem(notificationId));
    }

    @Test
    @Title("Уведомление не видно со страницы другого счетчика")
    public void testObjIdFilterEmptyResult() {
        superUser.onManagementSteps().onGrantsSteps().setGrantAndExpectSuccess(counterId, getGrant(SIMPLE));
        counterId2 = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getCounterWithBasicParameters())
                .getId();

        notificationsId = user.onManagementSteps().onNotificationsSteps()
                .getNotificationAndExpectSuccess(new NotificationsParameters()
                        .withLang("ru")
                        .withObjId(counterId2))
                .stream()
                .map(ExternalNotification::getId)
                .collect(Collectors.toList());

        assertThat("уведомление отсутствует в списке", notificationsId, not(hasItem(notificationId)));
    }

    @After
    public void teardown() {
        superUser.onInternalSteps().onNotificationSteps().deleteNotificationAndExpectSuccess(notificationId);
        otherUser.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId2);
    }
}
