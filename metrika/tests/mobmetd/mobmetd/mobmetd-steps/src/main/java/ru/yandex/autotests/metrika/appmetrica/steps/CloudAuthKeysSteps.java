package ru.yandex.autotests.metrika.appmetrica.steps;

import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationAppIdExportCloudKeyGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationAppIdExportCloudKeyIdDELETESchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationAppIdExportCloudKeyPOSTRequestSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationAppIdExportCloudKeyPOSTSchema;
import ru.yandex.autotests.metrika.appmetrica.errors.ManagementError;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.metrika.mobmet.cloud.model.CloudAuthKey;
import ru.yandex.metrika.mobmet.cloud.model.CloudAuthMaskedKey;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;
import java.util.List;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;

public class CloudAuthKeysSteps extends AppMetricaBaseSteps {

    public CloudAuthKeysSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить ключи сервисных аккаунтов для экспорта в облако для приложения {0}")
    @ParallelExecution(ALLOW)
    public List<CloudAuthMaskedKey> getCloudAuthKeysList(long appId) {
        ManagementV1ApplicationAppIdExportCloudKeyGETSchema result = get(
                ManagementV1ApplicationAppIdExportCloudKeyGETSchema.class,
                format("/management/v1/application/%s/export/cloud/key", appId));
        assertThat(SUCCESS_MESSAGE, result, expectSuccess());
        return result.getKeys();
    }

    @Step("Добавить ключ сервисного аккаунта для экспорта в облако для приложения {0}")
    @ParallelExecution(ALLOW)
    public CloudAuthKey createCloudAuthKey(long appId, CloudAuthKey key) {
        ManagementV1ApplicationAppIdExportCloudKeyPOSTSchema result = post(
                ManagementV1ApplicationAppIdExportCloudKeyPOSTSchema.class,
                format("/management/v1/application/%s/export/cloud/key", appId),
                new ManagementV1ApplicationAppIdExportCloudKeyPOSTRequestSchema().withKey(key)
        );

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getKey();
    }

    @Step("Добавить дубликат сервисного аккаунта для экспорта в облако для приложения {0} и получить ошибку")
    @ParallelExecution(ALLOW)
    public void createCloudAuthKeyAndExpectError(long appId, CloudAuthKey key, ManagementError error) {
        ManagementV1ApplicationAppIdExportCloudKeyPOSTSchema result = post(
                ManagementV1ApplicationAppIdExportCloudKeyPOSTSchema.class,
                format("/management/v1/application/%s/export/cloud/key", appId),
                new ManagementV1ApplicationAppIdExportCloudKeyPOSTRequestSchema().withKey(key)
        );

        assertThat(SUCCESS_MESSAGE, result, expectError(error));
    }

    @Step("Удалить ключ сервисного аккаунта {1} для экспорта в облако для приложения {0}")
    @ParallelExecution(ALLOW)
    public void deleteCloudAuthKey(long appId, long id) {
        ManagementV1ApplicationAppIdExportCloudKeyIdDELETESchema result = delete(
                ManagementV1ApplicationAppIdExportCloudKeyIdDELETESchema.class,
                format("/management/v1/application/%s/export/cloud/key/%s", appId, id)
        );

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());
    }
}