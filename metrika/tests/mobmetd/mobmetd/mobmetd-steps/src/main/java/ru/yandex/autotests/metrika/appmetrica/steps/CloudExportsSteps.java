package ru.yandex.autotests.metrika.appmetrica.steps;

import java.net.URL;

import com.google.common.collect.ImmutableSet;

import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.InternalManagementV1ApplicationAppIdExportCloudExportIdDELETESchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.InternalManagementV1ApplicationAppIdExportCloudExportIdDetailsGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.InternalManagementV1ApplicationAppIdExportCloudExportIdTableDELETESchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationAppIdExportCloudExportIdGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationAppIdExportCloudExportIdResumePUTSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationAppIdExportCloudExportIdStopPUTSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationAppIdExportCloudGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationAppIdExportCloudPOSTRequestSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationAppIdExportCloudPOSTSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationAppIdExportCloudValidatePUTRequestSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationAppIdExportCloudValidatePUTSchema;
import ru.yandex.autotests.metrika.appmetrica.errors.ManagementError;
import ru.yandex.autotests.metrika.appmetrica.parameters.CloudExportRequestParams;
import ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.metrika.mobmet.cloud.model.CloudExport;
import ru.yandex.metrika.mobmet.cloud.model.CloudExportAdapter;
import ru.yandex.metrika.mobmet.cloud.model.CloudExportDetails;
import ru.yandex.metrika.mobmet.cloud.model.ExportValidationResult;
import ru.yandex.qatools.allure.annotations.Step;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.TABLE_FOR_FUNCTIONAL_TESTS_ILLEGAL_SCHEMA;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.TABLE_FOR_FUNCTIONAL_TESTS_VALID_SCHEMA;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ANYTHING_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectAnything;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

public class CloudExportsSteps extends AppMetricaBaseSteps {

    private final static ImmutableSet<String> TEST_TABLES = ImmutableSet.of(
            TABLE_FOR_FUNCTIONAL_TESTS_VALID_SCHEMA,
            TABLE_FOR_FUNCTIONAL_TESTS_ILLEGAL_SCHEMA);

    public CloudExportsSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить список экспортов в облако для приложения {0}")
    @ParallelExecution(ALLOW)
    public ManagementV1ApplicationAppIdExportCloudGETSchema getCloudExportsList(long appId,
                                                                                CloudExportRequestParams requestParams) {
        ManagementV1ApplicationAppIdExportCloudGETSchema result = get(
                ManagementV1ApplicationAppIdExportCloudGETSchema.class,
                format("/management/v1/application/%s/export/cloud", appId),
                requestParams);
        assertThat(SUCCESS_MESSAGE, result, expectSuccess());
        return result;
    }

    @Step("Получить экспорт {1} для приложения {0}")
    @ParallelExecution(ALLOW)
    public CloudExportAdapter getCloudExport(long appId,
                                             long exportId) {
        ManagementV1ApplicationAppIdExportCloudExportIdGETSchema result = get(
                ManagementV1ApplicationAppIdExportCloudExportIdGETSchema.class,
                format("/management/v1/application/%s/export/cloud/%s", appId, exportId));
        assertThat(SUCCESS_MESSAGE, result, expectSuccess());
        return result.getExport();
    }

    @Step("Создать экспорт в облако для приложения {0}")
    @ParallelExecution(ALLOW)
    public CloudExport createCloudExport(long appId, CloudExport export) {
        ManagementV1ApplicationAppIdExportCloudPOSTSchema result = post(
                ManagementV1ApplicationAppIdExportCloudPOSTSchema.class,
                format("/management/v1/application/%s/export/cloud", appId),
                new ManagementV1ApplicationAppIdExportCloudPOSTRequestSchema().withExport(export)
        );

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getExport();
    }

    @Step("Создать экспорт в облако для приложения {0}  и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public void createCloudExportAndExpectError(long appId, CloudExport export, ManagementError error) {
        ManagementV1ApplicationAppIdExportCloudPOSTSchema result = post(
                ManagementV1ApplicationAppIdExportCloudPOSTSchema.class,
                format("/management/v1/application/%s/export/cloud", appId),
                new ManagementV1ApplicationAppIdExportCloudPOSTRequestSchema().withExport(export)
        );

        assertThat(ERROR_MESSAGE, result, expectError(error));
    }

    @Step("Валидировать экспорт в облако для приложения {0}")
    @ParallelExecution(ALLOW)
    public ExportValidationResult validate(long appId, CloudExport export) {
        ManagementV1ApplicationAppIdExportCloudValidatePUTSchema result = put(
                ManagementV1ApplicationAppIdExportCloudValidatePUTSchema.class,
                format("/management/v1/application/%s/export/cloud/validate", appId),
                new ManagementV1ApplicationAppIdExportCloudValidatePUTRequestSchema().withExport(export));
        return result.getResult();
    }

    @Step("Остановить экспорт в облако {1} для приложения {0}")
    @ParallelExecution(ALLOW)
    public void stopCloudExport(long appId, long id) {
        ManagementV1ApplicationAppIdExportCloudExportIdStopPUTSchema result = put(
                ManagementV1ApplicationAppIdExportCloudExportIdStopPUTSchema.class,
                format("/management/v1/application/%s/export/cloud/%s/stop", appId, id)
        );

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());
    }

    @Step("Возобновить экспорт в облако {1} для приложения {0}")
    @ParallelExecution(ALLOW)
    public void resumeCloudExport(long appId, long id) {
        ManagementV1ApplicationAppIdExportCloudExportIdResumePUTSchema result = put(
                ManagementV1ApplicationAppIdExportCloudExportIdResumePUTSchema.class,
                format("/management/v1/application/%s/export/cloud/%s/resume", appId, id)
        );

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());
    }

    @Step("Удалить данные об экспорте в облако {1} для приложения {0}")
    @ParallelExecution(ALLOW)
    public void deleteCloudExport(long appId, long id) {
        InternalManagementV1ApplicationAppIdExportCloudExportIdDELETESchema result = delete(
                InternalManagementV1ApplicationAppIdExportCloudExportIdDELETESchema.class,
                format("/internal/management/v1/application/%s/export/cloud/%s", appId, id)
        );

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());
    }

    @Step("Получить sql таблицы из облака для экспорта {1} для приложения {0}")
    @ParallelExecution(ALLOW)
    public CloudExportDetails showCloudExportCreateTableSql(long appId, long exportId) {
        InternalManagementV1ApplicationAppIdExportCloudExportIdDetailsGETSchema result = get(
                InternalManagementV1ApplicationAppIdExportCloudExportIdDetailsGETSchema.class,
                format("/internal/management/v1/application/%s/export/cloud/%s/details", appId, exportId));
        assertThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getDetails();
    }

    @Step("Удалить в облаке таблицу экспорта {1} для приложения {0}")
    @ParallelExecution(ALLOW)
    public void dropExportTableAndIgnoreResult(long appId, CloudExportAdapter export) {
        if (TEST_TABLES.contains(export.getClickhouseTableName())) {
            return;
        }

        InternalManagementV1ApplicationAppIdExportCloudExportIdTableDELETESchema result = delete(
                InternalManagementV1ApplicationAppIdExportCloudExportIdTableDELETESchema.class,
                format("/internal/management/v1/application/%s/export/cloud/%s/table", appId, export.getId()),
                new FreeFormParameters().append("serviceAccountId", export.getServiceAccountId()));
        assertThat(ANYTHING_MESSAGE, result, expectAnything());
    }

    public static CloudExportAdapter toAdapter(CloudExport cloudExport) {
        return new CloudExportAdapter()
                .withClickhouseTableName(cloudExport.getClickhouseTableName())
                .withClusterId(cloudExport.getClusterId())
                .withFields(cloudExport.getFields())
                .withFromDate(cloudExport.getFromDate())
                .withId(cloudExport.getId())
                .withMetaTableName(cloudExport.getMetaTableName())
                .withServiceAccountId(cloudExport.getServiceAccountId())
                .withStatus(cloudExport.getStatus())
                .withToDate(cloudExport.getToDate())
                .withType(cloudExport.getType());
    }
}
