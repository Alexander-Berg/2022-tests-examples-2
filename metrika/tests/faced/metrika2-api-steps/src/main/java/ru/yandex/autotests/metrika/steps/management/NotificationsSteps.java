package ru.yandex.autotests.metrika.steps.management;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1NotificationsGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1NotificationsIdDELETESchema;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.metrika.api.management.client.notification.ExternalNotification;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.List;

import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.Utils.aggregate;

/**
 * Created by sourx on 20.07.16.
 */
public class NotificationsSteps extends MetrikaBaseSteps {
    @Step("Получить уведомления")
    public List<ExternalNotification> getNotificationAndExpectSuccess(IFormParameters... parameters) {
        return getNotification(SUCCESS_MESSAGE, expectSuccess(), parameters);
    }

    private List<ExternalNotification> getNotification(String message, Matcher matcher,
                                                       IFormParameters... parameters) {
        ManagementV1NotificationsGETSchema result = executeAsJson(
                getRequestBuilder("/management/v1/notifications").get(parameters))
                .readResponse(ManagementV1NotificationsGETSchema.class);

        assertThat(message, result, matcher);

        return result.getNotifications();
    }

    @Step("Закрыть уведомление {0}")
    public Boolean deleteNotificationAndExpectSuccess(Long notificationId, IFormParameters... parameters) {
        if (notificationId == null) {
            return false;
        }

        return deleteNotification(SUCCESS_MESSAGE, expectSuccess(), notificationId, parameters);
    }

    @Step("Закрыть уведомление {1} и ожидать ошибку {0}")
    public Boolean deleteNotificationAndExpectError(IExpectedError error,
                                                    Long notificationId, IFormParameters... parameters) {
        if (notificationId == null) {
            return false;
        }

        return deleteNotification(ERROR_MESSAGE, expectError(error), notificationId, parameters);
    }

    private Boolean deleteNotification(String message, Matcher matcher,
                                       Long notificationId, IFormParameters... parameters) {
        ManagementV1NotificationsIdDELETESchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/notifications/%s", notificationId))
                        .delete(aggregate(parameters)))
                .readResponse(ManagementV1NotificationsIdDELETESchema.class);

        assertThat(message, result, matcher);

        return result.getSuccess();
    }
}
