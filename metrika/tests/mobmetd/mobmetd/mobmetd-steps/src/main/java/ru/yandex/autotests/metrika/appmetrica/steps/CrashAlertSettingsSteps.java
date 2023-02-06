package ru.yandex.autotests.metrika.appmetrica.steps;

import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.irt.testutils.allure.TestSteps;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.*;
import ru.yandex.autotests.metrika.appmetrica.errors.ManagementError;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.metrika.mobmet.crash.model.CrashAlertSettingsSummary;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;

public class CrashAlertSettingsSteps extends AppMetricaBaseSteps {
    public CrashAlertSettingsSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить настройки оповещений о крешах для приложения {0}")
    @ParallelExecution(ALLOW)
    public CrashAlertSettingsSummary get(long appId) {
        ManagementV1ApplicationAppIdCrashAlertsGETSchema result = get(
                ManagementV1ApplicationAppIdCrashAlertsGETSchema.class,
                format("/management/v1/application/%s/crash/alerts", appId));

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getAlertSettingsSummary();
    }

    @Step("Изменить настройки оповещений о крешах для приложения {0}")
    @ParallelExecution(ALLOW)
    public void update(long appId, CrashAlertSettingsSummary settingsSummary) {
        ManagementV1ApplicationAppIdCrashAlertsPUTSchema result = put(
                ManagementV1ApplicationAppIdCrashAlertsPUTSchema.class,
                format("/management/v1/application/%s/crash/alerts", appId),
                new ManagementV1ApplicationAppIdCrashAlertsPUTRequestSchema()
                        .withAlertSettingsSummary(settingsSummary)
        );

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());
    }

    @Step("Выслать повторно подтверждение email для приложения {0}")
    @ParallelExecution(ALLOW)
    public ManagementV1ApplicationAppIdCrashAlertsConfirmPUTSchema repeatConfirmation(long appId) {
        return put(
                ManagementV1ApplicationAppIdCrashAlertsConfirmPUTSchema.class,
                format("/management/v1/application/%s/crash/alerts/confirm", appId)
        );
    }

    @Step("Выслать повторно подтверждение email для приложения {0} и ожидать ошибку")
    @ParallelExecution(ALLOW)
    public void repeatConfirmationAndExpectError(long appId, ManagementError error) {
        ManagementV1ApplicationAppIdCrashAlertsConfirmPUTSchema result = put(
                ManagementV1ApplicationAppIdCrashAlertsConfirmPUTSchema.class,
                format("/management/v1/application/%s/crash/alerts/confirm", appId)
        );

        TestSteps.assertThat(ERROR_MESSAGE, result, expectError(error));
    }

    @Step("Изменить настройки оповещений о крешах для приложения {0} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public void updateAndExpectError(long appId, CrashAlertSettingsSummary settingsSummary, ManagementError error) {
        ManagementV1ApplicationAppIdCrashAlertsPUTSchema result = put(
                ManagementV1ApplicationAppIdCrashAlertsPUTSchema.class,
                format("/management/v1/application/%s/crash/alerts", appId),
                new ManagementV1ApplicationAppIdCrashAlertsPUTRequestSchema()
                        .withAlertSettingsSummary(settingsSummary)
        );

        TestSteps.assertThat(ERROR_MESSAGE, result, expectError(error));
    }

    @Step("Очистить настройки оповещений о крешах для приложения {0}")
    @ParallelExecution(ALLOW)
    public void clearSettings(long appId) {
        ManagementV1ApplicationAppIdCrashAlertsDELETESchema result = delete(
                ManagementV1ApplicationAppIdCrashAlertsDELETESchema.class,
                format("/management/v1/application/%s/crash/alerts", appId));

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());
    }
}
