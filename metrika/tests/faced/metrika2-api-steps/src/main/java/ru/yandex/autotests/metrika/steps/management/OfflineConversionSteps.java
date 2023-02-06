package ru.yandex.autotests.metrika.steps.management;

import org.apache.http.Consts;
import org.apache.http.HttpEntity;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.mime.MultipartEntityBuilder;
import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.beans.schemes.*;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.management.v1.offlineconversion.OfflineConversionType;
import ru.yandex.autotests.metrika.data.management.v1.offlineconversion.OfflineConversionUploadingData;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.autotests.metrika.utils.AllureUtils;
import ru.yandex.autotests.metrika.utils.CsvSerializer;
import ru.yandex.autotests.metrika.utils.EmptyHttpEntity;
import ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploading;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.List;

import static java.lang.String.format;
import static ru.yandex.autotests.httpclient.lite.core.BackEndRequestBuilder.EMPTY_CONTEXT;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

/**
 * @author zgmnkv
 */
public class OfflineConversionSteps extends MetrikaBaseSteps {

    private static final ContentType UPLOADING_CONTENT_TYPE = ContentType.create("text/csv", Consts.UTF_8);
    private static final String UPLOADING_PARAM_NAME = "file";
    private static final String UPLOADING_FILE_NAME = "data.csv";

    private CsvSerializer serializer = new CsvSerializer();

    @Step("Загрузить офлайн конверсии с типом {0}, для счетчика {1}")
    public OfflineConversionUploading upload(
            OfflineConversionType<?> type, Long counterId, String content, IFormParameters... parameters
    ) {
        return upload(SUCCESS_MESSAGE, expectSuccess(), counterId, type, content, parameters);
    }

    @Step("Загрузить офлайн конверсии с типом {0}, для счетчика {1}")
    public <T extends OfflineConversionUploadingData> OfflineConversionUploading upload(
            OfflineConversionType<T> type, Long counterId, List<T> data, IFormParameters... parameters
    ) {
        String content = serializer.serialize(type.getDataClass(), data);
        return upload(SUCCESS_MESSAGE, expectSuccess(), counterId, type, content, parameters);
    }

    @Step("Загрузить офлайн конверсии с типом {0}, для счетчика {1}, и ожидать ошибку {3}")
    public OfflineConversionUploading uploadAndExpectError(
            OfflineConversionType<?> type, Long counterId, String content, IExpectedError error, IFormParameters... parameters
    ) {
        return upload(ERROR_MESSAGE, expectError(error), counterId, type, content, parameters);
    }

    @Step("Загрузить офлайн конверсии с типом {0}, для счетчика {1}, и ожидать ошибку {3}")
    public <T extends OfflineConversionUploadingData> OfflineConversionUploading uploadAndExpectError(
            OfflineConversionType<T> type, Long counterId, List<T> data, IExpectedError error, IFormParameters... parameters
    ) {
        String content = serializer.serialize(type.getDataClass(), data);
        return upload(ERROR_MESSAGE, expectError(error), counterId, type, content, parameters);
    }

    @Step("Отправить не multipart запрос для счетчика {1}, и ожидать ошибку {2}")
    public void uploadNonMultipartAndExpectError(
            OfflineConversionType<?> type, Long counterId, IExpectedError error, IFormParameters... parameters
    ) {
        uploadNonMultipart(ERROR_MESSAGE, expectError(error), counterId, type, parameters);
    }

    @Step("Отправить запрос с неверным параметром для счетчика {1}, и ожидать ошибку {2}")
    public void uploadWrongPartAndExpectError(
            OfflineConversionType<?> type, Long counterId, IExpectedError error, IFormParameters... parameters
    ) {
        uploadWrongPart(ERROR_MESSAGE, expectError(error), counterId, type, parameters);
    }

    @Step("Получить загрузку офлайн конверсий {2} с типом {0} для счетчика {1}")
    public OfflineConversionUploading getUploading(OfflineConversionType<?> type, Long counterId, Long uploadingId) {
        ManagementV1CounterCounterIdOfflineConversionsUploadingIdGETSchema result = executeAsJson(
                getRequestBuilder(format(type.getFindByIdPath(), counterId, uploadingId)).get()
        ).readResponse(ManagementV1CounterCounterIdOfflineConversionsUploadingIdGETSchema.class);

        assumeThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getUploading();
    }

    @Step("Получить загрузки офлайн конверсий с типом {0} для счетчика {1}")
    public List<OfflineConversionUploading> getUploadings(OfflineConversionType<?> type, Long counterId) {
        ManagementV1CounterCounterIdOfflineConversionsUploadingsGETSchema result = executeAsJson(
                getRequestBuilder(format(type.getFindAllPath(), counterId)).get()
        ).readResponse(ManagementV1CounterCounterIdOfflineConversionsUploadingsGETSchema.class);

        assumeThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getUploadings();
    }

    @Step("Включить увеличенный период учёта конверсий с типом {0} для счетчика {1}")
    public Boolean enableExtendedThreshold(OfflineConversionType<?> type, Long counterId) {
        ManagementV1CounterCounterIdOfflineConversionsExtendedThresholdPOSTSchema result = executeAsJson(
                getRequestBuilder(format(type.getExtendedThresholdPath(), counterId)).post(new EmptyHttpEntity(), EMPTY_CONTEXT)
        ).readResponse(ManagementV1CounterCounterIdOfflineConversionsExtendedThresholdPOSTSchema.class);

        assumeThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getSuccess();
    }

    @Step("Выключить увеличенный период учёта конверсий с типом {0} для счетчика {1}")
    public Boolean disableExtendedThreshold(OfflineConversionType<?> type, Long counterId) {
        ManagementV1CounterCounterIdOfflineConversionsExtendedThresholdDELETESchema result = executeAsJson(
                getRequestBuilder(format(type.getExtendedThresholdPath(), counterId)).delete(EMPTY_CONTEXT)
        ).readResponse(ManagementV1CounterCounterIdOfflineConversionsExtendedThresholdDELETESchema.class);

        assumeThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getSuccess();
    }

    private OfflineConversionUploading upload(
            String message, Matcher matcher,
            Long counterId, OfflineConversionType<?> type, String content,
            IFormParameters... parameters
    ) {
        AllureUtils.addCsvAttachment("Содержимое загрузки", content.getBytes());

        HttpEntity entity = MultipartEntityBuilder.create()
                .addBinaryBody(UPLOADING_PARAM_NAME, content.getBytes(), UPLOADING_CONTENT_TYPE, UPLOADING_FILE_NAME)
                .build();

        ManagementV1CounterCounterIdOfflineConversionsUploadPOSTSchema result = executeAsJson(
                getRequestBuilder(format(type.getUploadPath(), counterId)).post(entity, parameters)
        ).readResponse(ManagementV1CounterCounterIdOfflineConversionsUploadPOSTSchema.class);

        assumeThat(message, result, matcher);

        return result.getUploading();
    }

    private void uploadNonMultipart(
            String message, Matcher matcher,
            Long counterId, OfflineConversionType<?> type,
            IFormParameters... parameters
    ) {
        ManagementV1CounterCounterIdOfflineConversionsUploadPOSTSchema result = executeAsJson(
                getRequestBuilder(format(type.getUploadPath(), counterId)).post(new EmptyHttpEntity(), parameters)
        ).readResponse(ManagementV1CounterCounterIdOfflineConversionsUploadPOSTSchema.class);

        assumeThat(message, result, matcher);
    }

    private void uploadWrongPart(
            String message, Matcher matcher,
            Long counterId, OfflineConversionType<?> type,
            IFormParameters... parameters
    ) {
        HttpEntity entity = MultipartEntityBuilder.create()
                .addBinaryBody("wrong", new byte[] {}, UPLOADING_CONTENT_TYPE, UPLOADING_FILE_NAME)
                .build();

        ManagementV1CounterCounterIdOfflineConversionsUploadPOSTSchema result = executeAsJson(
                getRequestBuilder(format(type.getUploadPath(), counterId)).post(entity, parameters)
        ).readResponse(ManagementV1CounterCounterIdOfflineConversionsUploadPOSTSchema.class);

        assumeThat(message, result, matcher);
    }
}
