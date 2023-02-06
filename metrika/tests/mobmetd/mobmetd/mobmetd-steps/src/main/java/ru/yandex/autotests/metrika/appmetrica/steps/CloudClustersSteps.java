package ru.yandex.autotests.metrika.appmetrica.steps;

import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.irt.testutils.allure.TestSteps;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationAppIdExportCloudClusterGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationAppIdExportCloudPOSTSchema;
import ru.yandex.autotests.metrika.appmetrica.errors.ManagementError;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.metrika.mobmet.cloud.model.CloudCluster;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;
import java.util.List;

import static java.lang.String.format;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;

public class CloudClustersSteps extends AppMetricaBaseSteps {
    public CloudClustersSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить список доступных кластеров в яндекс облаке для приложения {0} и сервисного аккаунта {1}")
    @ParallelExecution(ALLOW)
    public List<CloudCluster> getCloudClusters(long appId, String serviceAccountId) {
        ManagementV1ApplicationAppIdExportCloudClusterGETSchema result = get(
                ManagementV1ApplicationAppIdExportCloudClusterGETSchema.class,
                format("/management/v1/application/%s/export/cloud/cluster", appId),
                makeParameters("serviceAccountId", serviceAccountId));
        assertThat(SUCCESS_MESSAGE, result, expectSuccess());
        return result.getClusters();
    }

    @Step("Запросить список доступных кластеров в яндекс облаке для приложения {0} и сервисного аккаунта {1} и получить ошибку")
    @ParallelExecution(ALLOW)
    public void getCloudClustersAndExpectError(long appId, String serviceAccountId, ManagementError error) {
        ManagementV1ApplicationAppIdExportCloudPOSTSchema result = get(
                ManagementV1ApplicationAppIdExportCloudPOSTSchema.class,
                format("/management/v1/application/%s/export/cloud/cluster", appId),
                makeParameters("serviceAccountId", serviceAccountId));

        TestSteps.assertThat(ERROR_MESSAGE, result, expectError(error));

    }
}
