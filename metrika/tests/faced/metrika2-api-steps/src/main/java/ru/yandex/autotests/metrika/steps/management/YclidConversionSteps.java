package ru.yandex.autotests.metrika.steps.management;

import java.util.List;

import org.apache.http.Consts;
import org.apache.http.HttpEntity;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.mime.MultipartEntityBuilder;
import org.hamcrest.Matcher;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdYclidConversionsUploadPOSTSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdYclidConversionsUploadingIdGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdYclidConversionsUploadingsGETSchema;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.management.v1.yclidconversion.YclidConversionUploadingData;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.autotests.metrika.utils.AllureUtils;
import ru.yandex.autotests.metrika.utils.CsvSerializer;
import ru.yandex.autotests.metrika.utils.EmptyHttpEntity;
import ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploading;
import ru.yandex.qatools.allure.annotations.Step;

import static java.lang.String.format;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

public class YclidConversionSteps extends MetrikaBaseSteps {

    private static final ContentType UPLOADING_CONTENT_TYPE = ContentType.create("text/csv", Consts.UTF_8);
    private static final String UPLOADING_PARAM_NAME = "file";
    private static final String UPLOADING_FILE_NAME = "data.csv";
    private static final String YCLID_CONVERSIONS_UPLOAD_PATH = "/management/v1/counter/%s/yclid_conversions/upload";
    private static final String FIND_BY_ID_PATH = "/management/v1/counter/%s/yclid_conversions/uploading/%s";
    private static final String FIND_ALL_PATH = "/management/v1/counter/%s/yclid_conversions/uploadings";

    private CsvSerializer serializer = new CsvSerializer();

    @Step("Загрузить yclid конверсии для счетчика {0}")
    public OfflineConversionUploading upload(
            Long counterId, String content, IFormParameters... parameters
    ) {
        return upload(SUCCESS_MESSAGE, expectSuccess(), counterId, content, parameters);
    }

    @Step("Загрузить yclid конверсии для счетчика {0}")
    public OfflineConversionUploading upload(
            Long counterId, List<YclidConversionUploadingData> data, IFormParameters... parameters
    ) {
        String content = serializer.serialize(YclidConversionUploadingData.class, data);
        return upload(SUCCESS_MESSAGE, expectSuccess(), counterId, content, parameters);
    }

    @Step("Загрузить yclid конверсии для счетчика {0}, и ожидать ошибку {2}")
    public OfflineConversionUploading uploadAndExpectError(
            Long counterId, String content, IExpectedError error, IFormParameters... parameters
    ) {
        return upload(ERROR_MESSAGE, expectError(error), counterId, content, parameters);
    }

    private OfflineConversionUploading upload(
            String message, Matcher matcher,
            Long counterId, String content,
            IFormParameters... parameters
    ) {
        AllureUtils.addCsvAttachment("Содержимое загрузки", content.getBytes());

        HttpEntity entity = MultipartEntityBuilder.create()
                .addBinaryBody(UPLOADING_PARAM_NAME, content.getBytes(), UPLOADING_CONTENT_TYPE, UPLOADING_FILE_NAME)
                .build();

        ManagementV1CounterCounterIdYclidConversionsUploadPOSTSchema result = executeAsJson(
                getRequestBuilder(format(YCLID_CONVERSIONS_UPLOAD_PATH, counterId)).post(entity, parameters)
        ).readResponse(ManagementV1CounterCounterIdYclidConversionsUploadPOSTSchema.class);

        assumeThat(message, result, matcher);

        return result.getUploading();
    }

    @Step("Отправить не multipart запрос для счетчика {0}, и ожидать ошибку {1}")
    public void uploadNonMultipartAndExpectError(
            Long counterId, IExpectedError error, IFormParameters... parameters
    ) {
        uploadNonMultipart(ERROR_MESSAGE, expectError(error), counterId, parameters);
    }

    @Step("Получить загрузку yclid конверсий {1} для счетчика {0}")
    public OfflineConversionUploading getUploading(Long counterId, Long uploadingId) {
        ManagementV1CounterCounterIdYclidConversionsUploadingIdGETSchema result = executeAsJson(
                getRequestBuilder(format(FIND_BY_ID_PATH, counterId, uploadingId)).get()
        ).readResponse(ManagementV1CounterCounterIdYclidConversionsUploadingIdGETSchema.class);

        assumeThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getUploading();
    }

    @Step("Получить загрузки yclid конверсий для счетчика {0}")
    public List<OfflineConversionUploading> getUploadings(Long counterId) {
        ManagementV1CounterCounterIdYclidConversionsUploadingsGETSchema result = executeAsJson(
                getRequestBuilder(format(FIND_ALL_PATH, counterId)).get()
        ).readResponse(ManagementV1CounterCounterIdYclidConversionsUploadingsGETSchema.class);

        assumeThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getUploadings();
    }

    private void uploadNonMultipart(
            String message, Matcher matcher,
            Long counterId,
            IFormParameters... parameters
    ) {
        ManagementV1CounterCounterIdYclidConversionsUploadPOSTSchema result = executeAsJson(
                getRequestBuilder(format(YCLID_CONVERSIONS_UPLOAD_PATH, counterId)).post(new EmptyHttpEntity(), parameters)
        ).readResponse(ManagementV1CounterCounterIdYclidConversionsUploadPOSTSchema.class);

        assumeThat(message, result, matcher);
    }

}
