package ru.yandex.autotests.metrika.steps.management;

import com.google.common.collect.Lists;
import org.apache.http.HttpEntity;
import org.apache.http.NameValuePair;
import org.apache.http.message.BasicNameValuePair;
import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclient.lite.core.ResponseContent;
import ru.yandex.autotests.metrika.beans.schemes.*;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.parameters.management.v1.LogsApiParameters;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.autotests.metrika.utils.EmptyHttpEntity;
import ru.yandex.metrika.api.management.client.external.logs.LogRequest;
import ru.yandex.metrika.api.management.client.external.logs.LogRequestEvaluation;
import ru.yandex.metrika.api.management.client.external.logs.LogRequestSource;
import ru.yandex.metrika.api.management.client.external.logs.LogRequestStatus;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.Collections;
import java.util.List;
import java.util.concurrent.TimeUnit;

import static java.lang.String.format;
import static org.awaitility.Awaitility.await;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;


public class LogsApiSteps extends MetrikaBaseSteps {

    @Step("Получить запрос {1} логов для счетчика {0}")
    public LogRequest getLogRequest(Long counterId, Long requestId) {
        return executeAsJson(getRequestBuilder(format("/management/v1/counter/%s/logrequest/%s", counterId, requestId))
                .get())
                .readResponse(ManagementV1CounterCounterIdLogrequestRequestIdGETSchema.class).getLogRequest();
    }

    @Step("Получить запросы логов для счетчика {0}")
    public List<LogRequest> getLogRequests(Long counterId) {
        return getLogRequests(SUCCESS_MESSAGE, expectSuccess(), counterId).getRequests();
    }

    @Step("Получить запросы логов для счетчика {1} и ожидать ошибку {0}")
    public List<LogRequest> getUploadingsAndExpectError(IExpectedError error, Long counterId) {
        return getLogRequests(ERROR_MESSAGE, expectError(error), counterId).getRequests();
    }

    private ManagementV1CounterCounterIdLogrequestsGETSchema getLogRequests(String message, Matcher matcher, Long counterId) {
        ManagementV1CounterCounterIdLogrequestsGETSchema result = executeAsJson(
                getRequestBuilder(format("/management/v1/counter/%s/logrequests", counterId)).get())
                .readResponse(ManagementV1CounterCounterIdLogrequestsGETSchema.class);

        assertThat(message, result, matcher);
        return result;
    }

    @Step("Создать запрос логов для счетчика {0} в периоде {1} - {2} из {3}")
    public LogRequest createLogRequest(Long counterId, String date1, String date2, LogRequestSource source, String fields) {
        LogRequest logRequest = createLogRequest(SUCCESS_MESSAGE, expectSuccess(), counterId, date1, date2, source, fields).getLogRequest();
        assumeThat("вернулся корректный заказ логов", logRequest, notNullValue());
        return logRequest;
    }

    @Step("Создать запрос логов для счетчика {1} в периоде {2} - {3} из {4} и ожидать ошибку {0}")
    public void createLogRequestAndExpectError(IExpectedError error, Long counterId, String date1, String date2, LogRequestSource source, String fields) {
        createLogRequest(ERROR_MESSAGE, expectError(error), counterId, date1, date2, source, fields);
    }

    private ManagementV1CounterCounterIdLogrequestsPOSTSchema createLogRequest(String message, Matcher matcher, Long counterId, String date1, String date2, LogRequestSource source, String fields) {
        ManagementV1CounterCounterIdLogrequestsPOSTSchema result = executeAsJson(
                getRequestBuilder(format("/management/v1/counter/%s/logrequests", counterId))
                        .post(new EmptyHttpEntity(), new LogsApiParameters(date1, date2, source, fields)))
                .readResponse(ManagementV1CounterCounterIdLogrequestsPOSTSchema.class);

        assertThat(message, result, matcher);
        return result;
    }

    @Step("Скачать кусок {2} лога {1} для счетчика {0}")
    public ResponseContent download(Long counterId, Long requestId, Long partNumber) {
        return download(counterId, requestId, partNumber, Lists.newArrayList());
    }

    @Step("Скачать кусок {2} лога {1} для счетчика {0} в формате {3}")
    public ResponseContent download(Long counterId, Long requestId, Long partNumber, String format) {
        return download(counterId, requestId, partNumber, Lists.newArrayList(new BasicNameValuePair("format", format)));
    }

    private ResponseContent download(Long counterId, Long requestId, Long partNumber, List<NameValuePair> params) {
        return executeAsJson(getRequestBuilder(format("/management/v1/counter/%s/logrequest/%s/part/%s/download", counterId, requestId, partNumber))
                .get(params)
        ).getResponseContent();
    }

    @Step("Удалить лог {1} для счетчика {0}")
    public LogRequest clean(Long counterId, Long requestId) {
        return executeAsJson(getRequestBuilder(format("/management/v1/counter/%s/logrequest/%s/clean", counterId, requestId))
                .post(Collections.emptyList(), new IFormParameters[]{})
        ).readResponse(ManagementV1CounterCounterIdLogrequestRequestIdCleanPOSTSchema.class).getLogRequest();
    }

    @Step("Подождать обработки запроса {1} для счетчика {0}")
    public void waitForLogRequestProcessing(Long counterId, Long requestId) {
        await().atMost(10, TimeUnit.MINUTES)
                .pollInterval(15, TimeUnit.SECONDS)
                .until(() -> getLogRequests(counterId).stream()
                        .anyMatch(l -> l.getStatus() == LogRequestStatus.PROCESSED && l.getRequestId().equals(requestId)));
    }

    @Step("Отменить загрузку лога {1} для счетчика {0}")
    public LogRequest cancel(Long counterId, Long requestId) {
        return executeAsJson(getRequestBuilder(format("/management/v1/counter/%s/logrequest/%s/cancel", counterId, requestId))
                .post(Collections.emptyList(), new IFormParameters[]{})
        ).readResponse(ManagementV1CounterCounterIdLogrequestRequestIdCancelPOSTSchema.class).getLogRequest();
    }

    @Step("Оценить загрузку логов для счетчика {0} в периоде {1} - {2} из {3}")
    public LogRequestEvaluation evaluate(Long counterId, String date1, String date2, LogRequestSource source, String fields) {
        return executeAsJson(getRequestBuilder(format("/management/v1/counter/%s/logrequests/evaluate", counterId, date1, date2, source, fields))
                .get(new LogsApiParameters(date1, date2, source, fields)))
                .readResponse(ManagementV1CounterCounterIdLogrequestsEvaluateGETSchema.class).getLogRequestEvaluation();
    }
}
