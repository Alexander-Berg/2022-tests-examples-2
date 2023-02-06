package ru.yandex.autotests.metrika.steps.management;

import org.apache.http.HttpEntity;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.mime.MultipartEntityBuilder;
import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.beans.schemes.*;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.autotests.metrika.utils.AllureUtils;
import ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploading;
import ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploadingContentIdType;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.List;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.EMPTY;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;

/**
 * Created by konkov on 14.04.2016.
 */
public class UserParamsSteps extends MetrikaBaseSteps {

    private static final ContentType CONTENT_TYPE = ContentType.create("text/csv");
    private static final String UPLOADING_PARAM_NAME = "file";
    private static final String UPLOADING_FILE_NAME = "data.csv";

    @Step("Получить загрузки счетчика {0}")
    public List<UserParamsUploading> getUploadings(Long counterId) {
        return getUploadings(SUCCESS_MESSAGE, expectSuccess(), counterId).getUploadings();
    }

    @Step("Получить загрузки счетчика {1} и ожидать ошибку {0}")
    public List<UserParamsUploading> getUploadingsAndExpectError(IExpectedError error, Long counterId) {
        return getUploadings(ERROR_MESSAGE, expectError(error), counterId).getUploadings();
    }

    private ManagementV1CounterCounterIdUserParamsUploadingsGETSchema getUploadings(String message, Matcher matcher,
                                                                                    Long counterId) {
        ManagementV1CounterCounterIdUserParamsUploadingsGETSchema result = executeAsJson(
                getRequestBuilder(format("/management/v1/counter/%s/user_params/uploadings", counterId)).get())
                .readResponse(ManagementV1CounterCounterIdUserParamsUploadingsGETSchema.class);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Получить загрузку {1} счетчика {0}")
    public UserParamsUploading getUploading(Long counterId, Long uploadingId) {
        return getUploading(SUCCESS_MESSAGE, expectSuccess(), counterId, uploadingId).getUploading();
    }

    @Step("Получить загрузку {2} счетчика {1} и ожидать ошибку {0}")
    public UserParamsUploading getUploadingAndExpectError(IExpectedError error, Long counterId, Long uploadingId) {
        return getUploading(ERROR_MESSAGE, expectError(error), counterId, uploadingId).getUploading();
    }

    private ManagementV1CounterCounterIdUserParamsUploadingUploadingIdGETSchema getUploading(
            String message, Matcher matcher,
            Long counterId, Long uploadingId) {
        ManagementV1CounterCounterIdUserParamsUploadingUploadingIdGETSchema result = executeAsJson(
                getRequestBuilder(format("/management/v1/counter/%s/user_params/uploading/%s",
                        counterId, uploadingId)).get())
                .readResponse(ManagementV1CounterCounterIdUserParamsUploadingUploadingIdGETSchema.class);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Создать загрузку для счетчика {0}")
    public UserParamsUploading uploadFile(Long counterId, String content, IFormParameters... parameters) {
        return uploadFile(SUCCESS_MESSAGE, expectSuccess(), counterId, content, parameters).getUploading();
    }

    @Step("Создать загрузку для счетчика {1} и ожидать ошибку {0}")
    public UserParamsUploading uploadFileAndExpectError(IExpectedError error, Long counterId, String content,
                                                        IFormParameters... parameters) {
        return uploadFile(ERROR_MESSAGE, expectError(error), counterId, content, parameters).getUploading();
    }

    private ManagementV1CounterCounterIdUserParamsUploadingsUploadPOSTSchema uploadFile(
            String message, Matcher matcher, Long counterId, String content,
            IFormParameters... parameters) {
        AllureUtils.addCsvAttachment("Содержимое загрузки", content.getBytes());

        HttpEntity entity = MultipartEntityBuilder.create()
                .addBinaryBody(UPLOADING_PARAM_NAME, content.getBytes(), CONTENT_TYPE, UPLOADING_FILE_NAME)
                .build();

        ManagementV1CounterCounterIdUserParamsUploadingsUploadPOSTSchema result = executeAsJson(
                getRequestBuilder(format("/management/v1/counter/%s/user_params/uploadings/upload",
                        counterId)).post(entity, parameters))
                .readResponse(ManagementV1CounterCounterIdUserParamsUploadingsUploadPOSTSchema.class);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Изменить загрузку {1} счетчика {0}")
    public UserParamsUploading editUploading(Long counterId, Long uploadingId, UserParamsUploading uploading) {
        return editUploading(SUCCESS_MESSAGE, expectSuccess(), counterId, uploadingId, uploading).getUploading();
    }

    @Step("Изменить загрузку {2} счетчика {1} и ожидать ошибку {0}")
    public UserParamsUploading editUploadingAndExpectError(IExpectedError error,
                                                           Long counterId, Long uploadingId,
                                                           UserParamsUploading uploading) {
        return editUploading(ERROR_MESSAGE, expectError(error), counterId, uploadingId, uploading).getUploading();
    }

    private ManagementV1CounterCounterIdUserParamsUploadingUploadingIdPUTSchema editUploading(
            String message, Matcher matcher,
            Long counterId, Long uploadingId,
            UserParamsUploading uploading) {
        ManagementV1CounterCounterIdUserParamsUploadingUploadingIdPUTSchema result = executeAsJson(
                getRequestBuilder(format("/management/v1/counter/%s/user_params/uploading/%s",
                        counterId, uploadingId)).put(
                        new ManagementV1CounterCounterIdUserParamsUploadingUploadingIdPUTRequestSchema()
                                .withUploading(uploading), EMPTY))
                .readResponse(ManagementV1CounterCounterIdUserParamsUploadingUploadingIdPUTSchema.class);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Подтвердить загрузку {2} счетчика {0}")
    public UserParamsUploading confirm(Long counterId, UserParamsUploadingContentIdType contentIdType,
                                       UserParamsUploading uploading, IFormParameters... parameters) {
        return confirm(SUCCESS_MESSAGE, expectSuccess(), counterId, contentIdType, uploading, parameters)
                .getUploading();
    }

    private ManagementV1CounterCounterIdUserParamsUploadingUploadingIdConfirmPOSTSchema confirm(
            String message, Matcher matcher, Long counterId,
            UserParamsUploadingContentIdType contentIdType,
            UserParamsUploading uploading,
            IFormParameters... parameters) {
        ManagementV1CounterCounterIdUserParamsUploadingUploadingIdConfirmPOSTSchema result = executeAsJson(
                getRequestBuilder(format("/management/v1/counter/%s/user_params/uploading/%s/confirm",
                        counterId, uploading.getId())).post(
                        new ManagementV1CounterCounterIdUserParamsUploadingUploadingIdConfirmPOSTRequestSchema()
                                .withUploading(uploading.withContentIdType(contentIdType)), parameters))
                .readResponse(ManagementV1CounterCounterIdUserParamsUploadingUploadingIdConfirmPOSTSchema.class);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Загрузить файл и подтвердить загрузку для счетчика {0}")
    public UserParamsUploading uploadFileAndConfirm(Long counterId, UserParamsUploadingContentIdType contentIdType,
                                                    String content, IFormParameters... parameters) {
        UserParamsUploading uploading = uploadFile(counterId, content, parameters);
        return confirm(counterId, contentIdType, uploading, parameters);
    }

}
