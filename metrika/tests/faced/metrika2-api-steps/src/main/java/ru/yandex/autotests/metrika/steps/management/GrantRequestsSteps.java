package ru.yandex.autotests.metrika.steps.management;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.irt.testutils.allure.TestSteps;
import ru.yandex.autotests.metrika.beans.schemes.*;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.metrika.api.management.client.AddGrantRequest;
import ru.yandex.metrika.api.management.client.external.CounterGrantRequest;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.List;

import static java.util.Collections.singletonList;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;

/**
 * Created by konkov on 08.12.2015.
 */
public class GrantRequestsSteps extends MetrikaBaseSteps {

    @Step("Запросить разрешение")
    public void requestGrantAndExpectSuccess(AddGrantRequest grantRequest, IFormParameters... parameters) {
        requestGrant(SUCCESS_MESSAGE, expectSuccess(), grantRequest, parameters);
    }

    private void requestGrant(String message, Matcher matcher,
                              AddGrantRequest grantRequest, IFormParameters... parameters) {
        InternalGrantRequestsPOSTSchema result = executeAsJson(
                getRequestBuilder("/internal/grant_requests")
                        .post(new InternalGrantRequestsPOSTRequestSchema()
                                        .withRequests(singletonList(grantRequest)),
                                parameters))
                .readResponse(InternalGrantRequestsPOSTSchema.class);

        TestSteps.assertThat(message, result, matcher);
    }

    @Step("Получить список запросов на доступ счетчика {0}")
    public List<CounterGrantRequest> getGrantRequestsAndExpectSuccess(Long counterId,
                                                                      IFormParameters... parameters) {
        return getGrantRequests(SUCCESS_MESSAGE, expectSuccess(), counterId, parameters);
    }

    @Step("Получить список запросов на доступ счетчика {1} и ожидать ошибку {0}")
    public List<CounterGrantRequest> getGrantRequestsAndExpectError(IExpectedError error, Long counterId,
                                                                    IFormParameters... parameters) {
        return getGrantRequests(ERROR_MESSAGE, expectError(error), counterId, parameters);
    }

    private List<CounterGrantRequest> getGrantRequests(String message, Matcher matcher, Long counterId,
                                                             IFormParameters... parameters) {
        ManagementV1CounterCounterIdGrantRequestsGETSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/grant_requests", counterId))
                        .get(parameters))
                .readResponse(ManagementV1CounterCounterIdGrantRequestsGETSchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result.getGrantRequests();
    }

    @Step("Принять запрос на доступ к счетчику {0}")
    public void acceptGrantRequestAndExpectSuccess(Long counterId, CounterGrantRequest grantRequest,
                                                   IFormParameters... parameters) {
        acceptGrantRequest(SUCCESS_MESSAGE, expectSuccess(), counterId, grantRequest, parameters);
    }

    @Step("Принять запрос на доступ к счетчику {1} и ожидать ошибку {0}")
    public void acceptGrantRequestAndExpectError(IExpectedError error,
                                                 Long counterId, CounterGrantRequest grantRequest,
                                                 IFormParameters... parameters) {
        acceptGrantRequest(ERROR_MESSAGE, expectError(error), counterId, grantRequest, parameters);
    }

    private void acceptGrantRequest(String message, Matcher matcher,
                                    Long counterId, CounterGrantRequest grantRequest,
                                    IFormParameters... parameters) {
        ManagementV1CounterCounterIdGrantRequestAcceptPOSTSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/grant_request/accept", counterId))
                        .post(new ManagementV1CounterCounterIdGrantRequestAcceptPOSTRequestSchema()
                                        .withGrantRequest(grantRequest),
                                parameters))
                .readResponse(ManagementV1CounterCounterIdGrantRequestAcceptPOSTSchema.class);

        TestSteps.assertThat(message, result, matcher);
    }

    @Step("Отклонить запрос на доступ к счетчику {0}")
    public void rejectGrantRequestAndExpectSuccess(Long counterId, CounterGrantRequest grantRequest,
                                                   IFormParameters... parameters) {
        rejectGrantRequest(SUCCESS_MESSAGE, expectSuccess(), counterId, grantRequest, parameters);
    }

    @Step("Отклонить запрос на доступ к счетчику {1} и ожидать ошибку {0}")
    public void rejectGrantRequestAndExpectError(IExpectedError error,
                                                 Long counterId, CounterGrantRequest grantRequest,
                                                 IFormParameters... parameters) {
        rejectGrantRequest(ERROR_MESSAGE, expectError(error), counterId, grantRequest, parameters);
    }

    private void rejectGrantRequest(String message, Matcher matcher,
                                    Long counterId, CounterGrantRequest grantRequest,
                                    IFormParameters... parameters) {
        ManagementV1CounterCounterIdGrantRequestAcceptPOSTSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/grant_request/reject", counterId))
                        .post(new ManagementV1CounterCounterIdGrantRequestAcceptPOSTRequestSchema()
                                        .withGrantRequest(grantRequest),
                                parameters))
                .readResponse(ManagementV1CounterCounterIdGrantRequestAcceptPOSTSchema.class);

        TestSteps.assertThat(message, result, matcher);
    }
}
