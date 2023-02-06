package ru.yandex.autotests.audience.internal.api.steps;

import org.apache.commons.csv.CSVRecord;
import ru.yandex.autotests.audience.internal.api.schema.custom.SegmentDataSchema;
import ru.yandex.autotests.audience.internal.api.schema.custom.SegmentDataSchemaNegative;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.commons.clients.http.HttpClientLiteFacade;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;
import java.util.List;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;

/**
 * Created by apuzikov on 12.07.17.
 */
public class CryptaSteps extends HttpClientLiteFacade {

    public CryptaSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    //Warning: too heavy results
    @Step("Получить список сматченных кук по загруженному сегменту")
    public List<CSVRecord> getUsers(IFormParameters... parameters) {
        return get(SegmentDataSchema.class, "/crypta/users", parameters);
    }

    @Step("Получить список кук и ожидать ошибку {0}")
    public SegmentDataSchemaNegative getUsersAndExpectError(IExpectedError error, IFormParameters... parameters) {
        SegmentDataSchemaNegative result = get(SegmentDataSchemaNegative.class, "/crypta/users", parameters);

        assertThat(ERROR_MESSAGE, result, expectError(error));

        return result;
    }

    @Step("Получить данные crypta сегмента")
    public List<CSVRecord> getCryptaSegmentData(IFormParameters... parameters) {
        return get(SegmentDataSchema.class, "/crypta/crypta_segment_data", parameters);
    }

    @Step("Пытаться получить данные crypta сегмента, но получить ошибку {0}")
    public SegmentDataSchemaNegative getCryptaSegmentDataAndExpectError(IExpectedError error, IFormParameters... parameters) {
        SegmentDataSchemaNegative result = get(SegmentDataSchemaNegative.class, "/crypta/crypta_segment_data", parameters);

        assertThat(ERROR_MESSAGE, result, expectError(error));

        return result;
    }

    @Step("Получить данные uploading сегмента")
    public List<CSVRecord> getUploadingSegmentData(IFormParameters... parameters) {
        return get(SegmentDataSchema.class, "/crypta/uploading_segment_data", parameters);
    }

    @Step("Пытаться получить данные uploading сегмента, но получить ошибку {0}")
    public SegmentDataSchemaNegative getUploadingSegmentDataAndExpectError(IExpectedError error, IFormParameters... parameters) {
        SegmentDataSchemaNegative result = get(SegmentDataSchemaNegative.class, "/crypta/uploading_segment_data", parameters);

        assertThat(ERROR_MESSAGE, result, expectError(error));

        return result;
    }
}
