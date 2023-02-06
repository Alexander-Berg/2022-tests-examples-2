package ru.yandex.autotests.metrika.steps.management;

import java.util.List;
import java.util.Map;

import org.apache.http.Consts;
import org.apache.http.HttpEntity;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.mime.MultipartEntityBuilder;
import org.hamcrest.Matcher;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdExpenseColumnSettingsGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdExpenseUploadPOSTSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdExpenseUploadingUploadingIdGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdExpenseUploadingsGETSchema;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.autotests.metrika.utils.AllureUtils;
import ru.yandex.autotests.metrika.utils.CsvSerializer;
import ru.yandex.metrika.api.management.client.external.expense.ExpenseUploading;
import ru.yandex.metrika.api.management.client.uploading.ExpenseUploadingColumnSettings;
import ru.yandex.qatools.allure.annotations.Step;

import static java.lang.String.format;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

public class ExpenseSteps extends MetrikaBaseSteps {

    private static final ContentType UPLOADING_CONTENT_TYPE = ContentType.create("text/csv", Consts.UTF_8);
    private static final String UPLOADING_PARAM_NAME = "file";
    private static final String UPLOADING_FILE_NAME = "data.csv";
    private static final String UPLOAD_PATH = "/management/v1/counter/%s/expense/upload";
    private static final String UPLOAD_REMOVE_PATH = "/management/v1/counter/%s/expense/delete";
    private static final String FIND_BY_ID_PATH = "/management/v1/counter/%s/expense/uploading/%s";
    private static final String FIND_ALL_PATH = "/management/v1/counter/%s/expense/uploadings";
    private static final String FIND_SETTINGS_PATH = "/management/v1/counter/%s/expense/column_settings";

    private CsvSerializer serializer = new CsvSerializer();

    @Step("Загрузить расходы для счетчика {0}")
    public ExpenseUploading upload(
            Long counterId, String content, IFormParameters... parameters
    ) {
        return upload(SUCCESS_MESSAGE, expectSuccess(), counterId, content, parameters);
    }

    @Step("Загрузить удаления расходов для счетчика {0}")
    public ExpenseUploading remove(
            Long counterId, String content, IFormParameters... parameters
    ) {
        return remove(SUCCESS_MESSAGE, expectSuccess(), counterId, content, parameters);
    }

    @Step("Загрузить расходы для счетчика {0}, и ожидать ошибку {2}")
    public ExpenseUploading uploadAndExpectError(
            Long counterId, String content, IExpectedError error, IFormParameters... parameters
    ) {
        return upload(ERROR_MESSAGE, expectError(error), counterId, content, parameters);
    }

    @Step("Загрузить удаления расходов для счетчика {0}, и ожидать ошибку {2}")
    public ExpenseUploading removeAndExpectError(
            Long counterId, String content, IExpectedError error, IFormParameters... parameters
    ) {
        return remove(ERROR_MESSAGE, expectError(error), counterId, content, parameters);
    }

    @Step("Получить список настроек загрузок для счетчика {0}")
    public Map<String, ExpenseUploadingColumnSettings> getExpensesSettings(
            Long counterId
    ) {
        ManagementV1CounterCounterIdExpenseColumnSettingsGETSchema result = executeAsJson(
                getRequestBuilder(format(FIND_SETTINGS_PATH, counterId)).get()
        ).readResponse(ManagementV1CounterCounterIdExpenseColumnSettingsGETSchema.class);

        assumeThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getColumnSettings();
    }

    @Step("Получить загрузку расходов {1} для счетчика {0}")
    public ExpenseUploading getUploading(Long counterId, Long uploadingId) {
        ManagementV1CounterCounterIdExpenseUploadingUploadingIdGETSchema result = executeAsJson(
                getRequestBuilder(format(FIND_BY_ID_PATH, counterId, uploadingId)).get()
        ).readResponse(ManagementV1CounterCounterIdExpenseUploadingUploadingIdGETSchema.class);

        assumeThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getUploading();
    }

    @Step("Получить загрузки расходов для счетчика {0}")
    public List<ExpenseUploading> getUploadings(Long counterId) {
        ManagementV1CounterCounterIdExpenseUploadingsGETSchema result = executeAsJson(
                getRequestBuilder(format(FIND_ALL_PATH, counterId)).get()
        ).readResponse(ManagementV1CounterCounterIdExpenseUploadingsGETSchema.class);

        assumeThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getUploadings();
    }

    private ExpenseUploading upload(
            String message, Matcher matcher,
            Long counterId,
            String content,
            IFormParameters... parameters
    ) {
        return upload_data(UPLOAD_PATH, message, matcher, counterId, content, parameters);
    }

    private ExpenseUploading remove(
            String message, Matcher matcher,
            Long counterId,
            String content,
            IFormParameters... parameters
    ) {
        return upload_data(UPLOAD_REMOVE_PATH, message, matcher, counterId, content, parameters);
    }

    private ExpenseUploading upload_data(
            String request_url,
            String message, Matcher matcher,
            Long counterId,
            String content,
            IFormParameters... parameters
    ) {
        AllureUtils.addCsvAttachment("Содержимое загрузки", content.getBytes());

        HttpEntity entity = MultipartEntityBuilder.create()
                .addBinaryBody(UPLOADING_PARAM_NAME, content.getBytes(), UPLOADING_CONTENT_TYPE, UPLOADING_FILE_NAME)
                .build();

        ManagementV1CounterCounterIdExpenseUploadPOSTSchema result = executeAsJson(
                getRequestBuilder(format(request_url, counterId)).post(entity, parameters)
        ).readResponse(ManagementV1CounterCounterIdExpenseUploadPOSTSchema.class);

        assumeThat(message, result, matcher);

        return result.getUploading();
    }
}
