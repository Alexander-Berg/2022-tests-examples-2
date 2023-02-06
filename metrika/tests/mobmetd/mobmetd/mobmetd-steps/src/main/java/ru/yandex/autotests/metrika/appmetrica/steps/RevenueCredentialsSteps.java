package ru.yandex.autotests.metrika.appmetrica.steps;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.*;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.mobmet.revenue.model.RevenueAppStoreCredentials;
import ru.yandex.metrika.mobmet.revenue.model.RevenueGooglePlayCredentials;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;

public class RevenueCredentialsSteps extends AppMetricaBaseSteps {

    public RevenueCredentialsSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить информацию о данных валидации покупок в AppStore для приложения {0}")
    @ParallelExecution(ALLOW)
    public RevenueAppStoreCredentials getAppStoreCredentials(Long appId) {
        return getAppStoreCredentials(SUCCESS_MESSAGE, expectSuccess(), appId).getData();
    }

    @Step("Обновить информацию о данных валидации покупок в AppStore для приложения {0}")
    @ParallelExecution(ALLOW)
    public RevenueAppStoreCredentials updateAppStoreCredentials(Long appId, RevenueAppStoreCredentials credentials) {
        return updateAppStoreCredentials(SUCCESS_MESSAGE, expectSuccess(), appId, credentials).getData();
    }

    @Step("Обновить информацию о данных валидации покупок в AppStore для приложения {0} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public void updateAppStoreCredentialsAndExpectError(
            Long appId, RevenueAppStoreCredentials credentials, IExpectedError error) {
        updateAppStoreCredentials(SUCCESS_MESSAGE, expectError(error), appId, credentials);
    }

    @Step("Включить валидацию покупок в AppStore для приложения {0}")
    @ParallelExecution(ALLOW)
    public RevenueAppStoreCredentials enableAppStoreCredentials(Long appId) {
        return enableAppStoreCredentials(SUCCESS_MESSAGE, expectSuccess(), appId).getData();
    }

    @Step("Включить валидацию покупок в AppStore для приложения {0} и ожидать ошибку {1}")
    @ParallelExecution(ALLOW)
    public void enableAppStoreCredentialsAndExpectError(Long appId, IExpectedError error) {
        enableAppStoreCredentials(SUCCESS_MESSAGE, expectError(error), appId);
    }

    @Step("Выключить валидацию покупок в AppStore для приложения {0}")
    @ParallelExecution(ALLOW)
    public RevenueAppStoreCredentials disableAppStoreCredentials(Long appId) {
        return disableAppStoreCredentials(SUCCESS_MESSAGE, expectSuccess(), appId).getData();
    }

    @Step("Получить информацию о данных валидации покупок в GooglePlay для приложения {0}")
    @ParallelExecution(ALLOW)
    public RevenueGooglePlayCredentials getGooglePlayCredentials(Long appId) {
        return getGooglePlayCredentials(SUCCESS_MESSAGE, expectSuccess(), appId).getData();
    }

    @Step("Обновить информацию о данных валидации покупок в GooglePlay для приложения {0}")
    @ParallelExecution(ALLOW)
    public RevenueGooglePlayCredentials updateGooglePlayCredentials(Long appId, RevenueGooglePlayCredentials credentials) {
        return updateGooglePlayCredentials(SUCCESS_MESSAGE, expectSuccess(), appId, credentials).getData();
    }

    @Step("Обновить информацию о данных валидации покупок в GooglePlay для приложения {0} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public void updateGooglePlayCredentialsAndExpectError(
            Long appId, RevenueGooglePlayCredentials credentials, IExpectedError error) {
        updateGooglePlayCredentials(SUCCESS_MESSAGE, expectError(error), appId, credentials);
    }

    @Step("Включить валидацию покупок в GooglePlay для приложения {0}")
    @ParallelExecution(ALLOW)
    public RevenueGooglePlayCredentials enableGooglePlayCredentials(Long appId) {
        return enableGooglePlayCredentials(SUCCESS_MESSAGE, expectSuccess(), appId).getData();
    }

    @Step("Включить валидацию покупок в GooglePlay для приложения {0} и ожидать ошибку {1}")
    @ParallelExecution(ALLOW)
    public void enableGooglePlayCredentialsAndExpectError(Long appId, IExpectedError error) {
        enableGooglePlayCredentials(SUCCESS_MESSAGE, expectError(error), appId);
    }

    @Step("Выключить валидацию покупок в GooglePlay для приложения {0}")
    @ParallelExecution(ALLOW)
    public RevenueGooglePlayCredentials disableGooglePlayCredentials(Long appId) {
        return disableGooglePlayCredentials(SUCCESS_MESSAGE, expectSuccess(), appId).getData();
    }

    private ManagementV1ApplicationAppIdRevenueCredentialsAppstoreGETSchema getAppStoreCredentials(
            String message, Matcher matcher, Long appId) {
        ManagementV1ApplicationAppIdRevenueCredentialsAppstoreGETSchema result = get(
                ManagementV1ApplicationAppIdRevenueCredentialsAppstoreGETSchema.class,
                format("/management/v1/application/%s/revenue/credentials/appstore", appId));
        assertThat(message, result, matcher);
        return result;
    }

    private ManagementV1ApplicationAppIdRevenueCredentialsAppstorePOSTSchema updateAppStoreCredentials(
            String message, Matcher matcher, Long appId, RevenueAppStoreCredentials credentials) {
        ManagementV1ApplicationAppIdRevenueCredentialsAppstorePOSTSchema result = post(
                ManagementV1ApplicationAppIdRevenueCredentialsAppstorePOSTSchema.class,
                format("/management/v1/application/%s/revenue/credentials/appstore", appId),
                credentials);
        assertThat(message, result, matcher);
        return result;
    }

    private ManagementV1ApplicationAppIdRevenueCredentialsAppstoreEnablePOSTSchema enableAppStoreCredentials(
            String message, Matcher matcher, Long appId) {
        ManagementV1ApplicationAppIdRevenueCredentialsAppstoreEnablePOSTSchema result = post(
                ManagementV1ApplicationAppIdRevenueCredentialsAppstoreEnablePOSTSchema.class,
                format("/management/v1/application/%s/revenue/credentials/appstore/enable", appId));
        assertThat(message, result, matcher);
        return result;
    }

    private ManagementV1ApplicationAppIdRevenueCredentialsAppstoreDisablePOSTSchema disableAppStoreCredentials(
            String message, Matcher matcher, Long appId) {
        ManagementV1ApplicationAppIdRevenueCredentialsAppstoreDisablePOSTSchema result = post(
                ManagementV1ApplicationAppIdRevenueCredentialsAppstoreDisablePOSTSchema.class,
                format("/management/v1/application/%s/revenue/credentials/appstore/disable", appId));
        assertThat(message, result, matcher);
        return result;
    }

    private ManagementV1ApplicationAppIdRevenueCredentialsGoogleplayGETSchema getGooglePlayCredentials(
            String message, Matcher matcher, Long appId) {
        ManagementV1ApplicationAppIdRevenueCredentialsGoogleplayGETSchema result = get(
                ManagementV1ApplicationAppIdRevenueCredentialsGoogleplayGETSchema.class,
                format("/management/v1/application/%s/revenue/credentials/googleplay", appId));
        assertThat(message, result, matcher);
        return result;
    }

    private ManagementV1ApplicationAppIdRevenueCredentialsGoogleplayPOSTSchema updateGooglePlayCredentials(
            String message, Matcher matcher, Long appId, RevenueGooglePlayCredentials credentials) {
        ManagementV1ApplicationAppIdRevenueCredentialsGoogleplayPOSTSchema result = post(
                ManagementV1ApplicationAppIdRevenueCredentialsGoogleplayPOSTSchema.class,
                format("/management/v1/application/%s/revenue/credentials/googleplay", appId),
                credentials);
        assertThat(message, result, matcher);
        return result;
    }

    private ManagementV1ApplicationAppIdRevenueCredentialsGoogleplayEnablePOSTSchema enableGooglePlayCredentials(
            String message, Matcher matcher, Long appId) {
        ManagementV1ApplicationAppIdRevenueCredentialsGoogleplayEnablePOSTSchema result = post(
                ManagementV1ApplicationAppIdRevenueCredentialsGoogleplayEnablePOSTSchema.class,
                format("/management/v1/application/%s/revenue/credentials/googleplay/enable", appId));
        assertThat(message, result, matcher);
        return result;
    }

    private ManagementV1ApplicationAppIdRevenueCredentialsGoogleplayDisablePOSTSchema disableGooglePlayCredentials(
            String message, Matcher matcher, Long appId) {
        ManagementV1ApplicationAppIdRevenueCredentialsGoogleplayDisablePOSTSchema result = post(
                ManagementV1ApplicationAppIdRevenueCredentialsGoogleplayDisablePOSTSchema.class,
                format("/management/v1/application/%s/revenue/credentials/googleplay/disable", appId));
        assertThat(message, result, matcher);
        return result;
    }
}