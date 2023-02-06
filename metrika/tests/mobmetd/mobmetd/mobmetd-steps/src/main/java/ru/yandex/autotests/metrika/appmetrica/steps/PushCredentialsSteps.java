package ru.yandex.autotests.metrika.appmetrica.steps;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.*;
import ru.yandex.autotests.metrika.appmetrica.body.MultipartFormBody;
import ru.yandex.autotests.metrika.appmetrica.info.push.credentials.AppleCredentialsInfo;
import ru.yandex.autotests.metrika.appmetrica.parameters.push.credentials.*;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.mobmet.push.response.PushCredentialsSummary;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;


/**
 * @author dancingelf
 */
public class PushCredentialsSteps extends AppMetricaBaseSteps {

    public PushCredentialsSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить информацию о данных авторизации приложения {0} на сервисах рассылки пушей")
    @ParallelExecution(ALLOW)
    public PushCredentialsSummary getCredentialsSummary(Long appId) {
        return getCredentialsSummary(SUCCESS_MESSAGE, expectSuccess(), appId).getPushCredentials();
    }


    @Step("Обновить данные FCM для приложения {0} значением {1}")
    @ParallelExecution(ALLOW)
    public PushCredentialsSummary updateAndroidCredentials(Long appId, AndroidUpdateParameters credentials) {
        return updateAndroidCredentials(SUCCESS_MESSAGE, expectSuccess(), appId, credentials).getPushCredentials();
    }

    @Step("Обновить данные FCM для приложения {0} значением {1} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public void updateAndroidCredentialsAndExpectError(Long appId, AndroidUpdateParameters credentials, IExpectedError error) {
        updateAndroidCredentials(ERROR_MESSAGE, expectError(error), appId, credentials);
    }

    @Step("Удалить учетные данные FCM для приложения {0}")
    @ParallelExecution(ALLOW)
    public PushCredentialsSummary deleteAndroidCredentials(Long appId) {
        return deleteAndroidCredentials(SUCCESS_MESSAGE, expectSuccess(), appId).getPushCredentials();
    }

    @Step("Удалить учетные данные FCM для приложения {0} и игнорировать результат")
    @ParallelExecution(ALLOW)
    public void deleteAndroidCredentialsIgnoringResult(Long appId) {
        deleteAndroidCredentials(ANYTHING_MESSAGE, expectAnything(), appId);
    }

    @Step("Обновить данные Apple для приложения {0} значением {1}")
    @ParallelExecution(ALLOW)
    public PushCredentialsSummary updateAppleCredentials(Long appId, AppleCredentialsInfo data) {
        return updateAppleCredentials(SUCCESS_MESSAGE, expectSuccess(), appId, data).getPushCredentials();
    }

    @Step("Обновить данные Apple для приложения {0} значением {1} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public void updateAppleCredentialsAndExpectError(Long appId, AppleCredentialsInfo data, IExpectedError error) {
        updateAppleCredentials(ERROR_MESSAGE, expectError(error), appId, data);
    }

    @Step("Удалить учетные данные Apple для приложения {0} с типом сертификата {1}")
    @ParallelExecution(ALLOW)
    public PushCredentialsSummary deleteAppleCredentials(Long appId, String certType) {
        return deleteAppleCredentials(SUCCESS_MESSAGE, expectSuccess(), appId, certType).getPushCredentials();
    }

    @Step("Удалить учетные данные Apple для приложения {0} с типом сертификата {1} и игнорировать результат")
    @ParallelExecution(ALLOW)
    public void deleteAppleCredentialsIgnoringResult(Long appId, String certType) {
        deleteAppleCredentials(ANYTHING_MESSAGE, expectAnything(), appId, certType);
    }

    @Step("Обновить учетные данные Huawei для приложения {0} значением {1}")
    @ParallelExecution(ALLOW)
    public PushCredentialsSummary updateHuaweiCredentials(Long appId, HuaweiUpdateParameters credentials) {
        return updateHuaweiCredentials(SUCCESS_MESSAGE, expectSuccess(), appId, credentials).getPushCredentials();
    }

    @Step("Обновить учетные данные Huawei для приложения {0} значением {1} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public void updateHuaweiCredentialsAndExpectError(Long appId, HuaweiUpdateParameters credentials, IExpectedError error) {
        updateHuaweiCredentials(ERROR_MESSAGE, expectError(error), appId, credentials);
    }

    @Step("Удалить учетные данные Huawei для приложения {0}")
    @ParallelExecution(ALLOW)
    public PushCredentialsSummary deleteHuaweiCredentials(Long appId) {
        return deleteHuaweiCredentials(SUCCESS_MESSAGE, expectSuccess(), appId).getPushCredentials();
    }

    @Step("Удалить учетные данные Huawei для приложения {0} и игнорировать результат")
    @ParallelExecution(ALLOW)
    public void deleteHuaweiCredentialsIgnoringResult(Long appId) {
        deleteHuaweiCredentials(ANYTHING_MESSAGE, expectAnything(), appId);
    }

    @Step("Обновить учетные winphone для приложения {0} значением {1}")
    @ParallelExecution(ALLOW)
    public PushCredentialsSummary updateWinCredentials(Long appId, WinUpdateParameters credentials) {
        return updateWinCredentials(SUCCESS_MESSAGE, expectSuccess(), appId, credentials).getPushCredentials();
    }

    @Step("Обновить учетные winphone для приложения {0} значением {1} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public void updateWinCredentialsAndExpectError(Long appId, WinUpdateParameters credentials, IExpectedError error) {
        updateWinCredentials(ERROR_MESSAGE, expectError(error), appId, credentials);
    }

    @Step("Удалить учетные данные winphone для приложения {0}")
    @ParallelExecution(ALLOW)
    public PushCredentialsSummary deleteWinCredentials(Long appId) {
        return deleteWinCredentials(SUCCESS_MESSAGE, expectSuccess(), appId).getPushCredentials();
    }

    @Step("Удалить учетные данные winphone для приложения {0} и игнорировать результат")
    @ParallelExecution(ALLOW)
    public void deleteWinCredentialsIgnoringResult(Long appId) {
        deleteWinCredentials(ANYTHING_MESSAGE, expectAnything(), appId);
    }

    private ManagementV1ApplicationAppIdPushCredentialsGETSchema getCredentialsSummary(
            String message, Matcher matcher, Long appId) {
        ManagementV1ApplicationAppIdPushCredentialsGETSchema result = get(
                ManagementV1ApplicationAppIdPushCredentialsGETSchema.class,
                format("/management/v1/application/%s/push/credentials", appId));
        assertThat(message, result, matcher);
        return result;
    }

    private ManagementV1ApplicationAppIdPushCredentialsAndroidPOSTSchema updateAndroidCredentials(
            String message, Matcher matcher, Long appId, AndroidUpdateParameters credentials) {
        ManagementV1ApplicationAppIdPushCredentialsAndroidPOSTSchema result = post(
                ManagementV1ApplicationAppIdPushCredentialsAndroidPOSTSchema.class,
                format("/management/v1/application/%s/push/credentials/android", appId),
                credentials);
        assertThat(message, result, matcher);
        return result;
    }

    private ManagementV1ApplicationAppIdPushCredentialsAndroidDELETESchema deleteAndroidCredentials(
            String message, Matcher matcher, Long appId) {
        ManagementV1ApplicationAppIdPushCredentialsAndroidDELETESchema result = delete(
                ManagementV1ApplicationAppIdPushCredentialsAndroidDELETESchema.class,
                format("/management/v1/application/%s/push/credentials/android", appId));
        assertThat(message, result, matcher);
        return result;
    }


    private ManagementV1ApplicationAppIdPushCredentialsIosPOSTSchema updateAppleCredentials(
            String message, Matcher matcher, Long appId, AppleCredentialsInfo data) {
        ManagementV1ApplicationAppIdPushCredentialsIosPOSTSchema result = post(
                ManagementV1ApplicationAppIdPushCredentialsIosPOSTSchema.class,
                format("/management/v1/application/%s/push/credentials/ios", appId),
                new MultipartFormBody("cert_file", data.getCertFile()),
                new AppleUpdateParameters(data.getPassword(), data.getCertType()));
        assertThat(message, result, matcher);
        return result;
    }

    private ManagementV1ApplicationAppIdPushCredentialsIosDELETESchema deleteAppleCredentials(
            String message, Matcher matcher, Long appId, String certType) {
        ManagementV1ApplicationAppIdPushCredentialsIosDELETESchema result = delete(
                ManagementV1ApplicationAppIdPushCredentialsIosDELETESchema.class,
                format("/management/v1/application/%s/push/credentials/ios", appId),
                new AppleDeleteParameters(certType));
        assertThat(message, result, matcher);
        return result;
    }

    private ManagementV1ApplicationAppIdPushCredentialsHuaweiPOSTSchema updateHuaweiCredentials(
            String message, Matcher matcher, Long appId, HuaweiUpdateParameters credentials) {
        ManagementV1ApplicationAppIdPushCredentialsHuaweiPOSTSchema result = post(
                ManagementV1ApplicationAppIdPushCredentialsHuaweiPOSTSchema.class,
                format("/management/v1/application/%s/push/credentials/huawei", appId),
                credentials);
        assertThat(message, result, matcher);
        return result;
    }

    private ManagementV1ApplicationAppIdPushCredentialsHuaweiDELETESchema deleteHuaweiCredentials(
            String message, Matcher matcher, Long appId) {
        ManagementV1ApplicationAppIdPushCredentialsHuaweiDELETESchema result = delete(
                ManagementV1ApplicationAppIdPushCredentialsHuaweiDELETESchema.class,
                format("/management/v1/application/%s/push/credentials/huawei", appId));
        assertThat(message, result, matcher);
        return result;
    }

    private ManagementV1ApplicationAppIdPushCredentialsWinphonePOSTSchema updateWinCredentials(
            String message, Matcher matcher, Long appId, WinUpdateParameters credentials) {
        ManagementV1ApplicationAppIdPushCredentialsWinphonePOSTSchema result = post(
                ManagementV1ApplicationAppIdPushCredentialsWinphonePOSTSchema.class,
                format("/management/v1/application/%s/push/credentials/winphone", appId),
                credentials);
        assertThat(message, result, matcher);
        return result;
    }

    private ManagementV1ApplicationAppIdPushCredentialsWinphoneDELETESchema deleteWinCredentials(
            String message, Matcher matcher, Long appId) {
        ManagementV1ApplicationAppIdPushCredentialsWinphoneDELETESchema result = delete(
                ManagementV1ApplicationAppIdPushCredentialsWinphoneDELETESchema.class,
                format("/management/v1/application/%s/push/credentials/winphone", appId));
        assertThat(message, result, matcher);
        return result;
    }
}
