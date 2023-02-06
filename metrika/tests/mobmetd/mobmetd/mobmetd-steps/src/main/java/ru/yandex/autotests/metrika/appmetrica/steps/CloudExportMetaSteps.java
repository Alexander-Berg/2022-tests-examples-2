package ru.yandex.autotests.metrika.appmetrica.steps;

import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationAppIdExportCloudTablesGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ExportCloudTableFieldsGETSchema;
import ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.metrika.mobmet.cloud.model.CloudExportFieldMeta;
import ru.yandex.metrika.mobmet.cloud.model.CloudTable;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;
import java.util.List;

import static java.lang.String.format;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

public class CloudExportMetaSteps extends AppMetricaBaseSteps {

    public static String CLIENT_EVENTS_TABLE = "client_events";

    public CloudExportMetaSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить список экспортов в облако для приложения {0}")
    @ParallelExecution(ALLOW)
    public List<CloudExportFieldMeta> getCloudExportFields() {
        ManagementV1ExportCloudTableFieldsGETSchema result = get(
                ManagementV1ExportCloudTableFieldsGETSchema.class,
                "/management/v1/export/cloud/table/fields");
        assertThat(SUCCESS_MESSAGE, result, expectSuccess());
        return result.getFields();
    }

    @Step("Получить список таблиц в облако для приложения {0} и сервисного аккаунта {1} в облаке {2}")
    @ParallelExecution(ALLOW)
    public List<CloudTable> getTables(long appId, String serviceAccountId, String clusterId) {
        ManagementV1ApplicationAppIdExportCloudTablesGETSchema result = get(
                ManagementV1ApplicationAppIdExportCloudTablesGETSchema.class,
                format("/management/v1/application/%s/export/cloud/tables", appId),
                new FreeFormParameters()
                        .append("serviceAccountId", serviceAccountId)
                        .append("clusterId", clusterId));
        assertThat(SUCCESS_MESSAGE, result, expectSuccess());
        return result.getTables();
    }
}
