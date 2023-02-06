package ru.yandex.autotests.metrika.steps.internal;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.beans.schemes.*;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.metrika.api.management.client.notification.Notification;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.List;

import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.Utils.aggregate;

/**
 * Created by sourx on 20.07.16.
 */
public class NotificationsSteps extends MetrikaBaseSteps {

    @Step("Получить список уведомлений")
    public List<Notification> getNotifications(IFormParameters... parameters) {
        return getAvailableNotifications(SUCCESS_MESSAGE, expectSuccess(), parameters);
    }

    @Step("Получить список уведомлений и ожидать ошибку {0}")
    public List<Notification> getNotificationsAndExpectError(IExpectedError error, IFormParameters... parameters) {
        return getAvailableNotifications(ERROR_MESSAGE, expectError(error), parameters);
    }

    private List<Notification> getAvailableNotifications(String message, Matcher matcher,
                                                         IFormParameters... parameters) {
        InternalAdminNotificationsGETSchema result = executeAsJson(
                getRequestBuilder("/internal/admin/notifications").get(parameters))
                .readResponse(InternalAdminNotificationsGETSchema.class);

        assertThat(message, result, matcher);

        return result.getNotifications();
    }

    @Step("Получить уведомление {0}")
    public Notification getNotificationAndExpextSuccess(Long notificationId, IFormParameters... parameters) {
        return getNotification(SUCCESS_MESSAGE, expectSuccess(), notificationId, parameters);
    }

    @Step("Получить уведомление {1} и ожидать ошибку {0}")
    public Notification getNotificationAndExpectError(IExpectedError error,
                                                      Long notificationId,
                                                      IFormParameters... parameters) {
        return getNotification(ERROR_MESSAGE, expectError(error), notificationId, parameters);
    }

    private Notification getNotification(String message,
                                         Matcher matcher,
                                         Long notificationId,
                                         IFormParameters... parameters) {
        InternalAdminNotificationsIdGETSchema result = executeAsJson(
                getRequestBuilder(String.format("/internal/admin/notifications/%s", notificationId)).get(parameters))
                .readResponse(InternalAdminNotificationsIdGETSchema.class);

        assertThat(message, result, matcher);

        return result.getNotification();
    }

    @Step("Добавить уведомление")
    public Notification addNotificationAndExpectSuccess(Notification notification, IFormParameters... parameters) {
        return addNotification(SUCCESS_MESSAGE, expectSuccess(), notification, parameters);
    }

    @Step("Добавить уведомление и ожидать ошибку {0}")
    public Notification addNotificationAndExpectError(IExpectedError error,
                                                      Notification notification,
                                                      IFormParameters... parameters) {
        return addNotification(ERROR_MESSAGE, expectError(error), notification, parameters);
    }

    private Notification addNotification(String message,
                                         Matcher matcher,
                                         Notification notification,
                                         IFormParameters... parameters) {
        InternalAdminNotificationsPOSTSchema result = executeAsJson(
                getRequestBuilder("/internal/admin/notifications")
                        .post(
                                new InternalAdminNotificationsPOSTRequestSchema()
                                        .withNotification(notification), parameters))
                .readResponse(InternalAdminNotificationsPOSTSchema.class);

        assertThat(message, result, matcher);

        return result.getNotification();
    }

    @Step("Изменить уведомление {0}")
    public Notification editNotificationAndExpectSuccess(Long notificationId,
                                                         Notification notification,
                                                         IFormParameters... parameters) {
        return editNotification(SUCCESS_MESSAGE, expectSuccess(), notificationId, notification, parameters);
    }

    @Step("Изменить уведомление {1} и ожидать ошибку {0}")
    public Notification editNotificationAndExpectError(IExpectedError error,
                                                       Long notificationId,
                                                       Notification notification,
                                                       IFormParameters... parameters) {

        return editNotification(ERROR_MESSAGE, expectError(error), notificationId, notification, parameters);
    }

    private Notification editNotification(String message,
                                          Matcher matcher,
                                          Long notificationId,
                                          Notification notification,
                                          IFormParameters... parameters) {
        InternalAdminNotificationsIdPUTSchema result = executeAsJson(
                getRequestBuilder(String.format("/internal/admin/notifications/%s", notificationId))
                        .put(new InternalAdminNotificationsPOSTRequestSchema()
                                .withNotification(notification), parameters))
                .readResponse(InternalAdminNotificationsIdPUTSchema.class);

        assertThat(message, result, matcher);

        return result.getNotification();
    }

    @Step("Удалить уведомление {0}")
    public Boolean deleteNotificationAndExpectSuccess(Long notificationId) {
        if (notificationId == null) {
            return false;
        }

        return deleteNotification(SUCCESS_MESSAGE, expectSuccess(), notificationId);
    }

    @Step("Удалить уведомление {1} и ожидать ошибку {0}")
    public Boolean deleteNotificationAndExpectError(IExpectedError error, Long notificationId) {
        if (notificationId == null) {
            return false;
        }

        return deleteNotification(ERROR_MESSAGE, expectError(error), notificationId);
    }

    private Boolean deleteNotification(String message,
                                       Matcher matcher,
                                       Long notificationId,
                                       IFormParameters... parameters) {
        InternalAdminNotificationsIdDELETESchema result = executeAsJson(
                getRequestBuilder(String.format("/internal/admin/notifications/%s", notificationId))
                        .delete(aggregate(parameters)))
                .readResponse(InternalAdminNotificationsIdDELETESchema.class);

        assertThat(message, result, matcher);

        return result.getSuccess();
    }
}
