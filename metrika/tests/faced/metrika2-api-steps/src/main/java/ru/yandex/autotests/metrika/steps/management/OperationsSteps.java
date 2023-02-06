package ru.yandex.autotests.metrika.steps.management;

import org.hamcrest.Matcher;
import ru.yandex.autotests.irt.testutils.json.JsonUtils;
import ru.yandex.autotests.metrika.beans.schemes.*;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.core.response.MetrikaJsonResponse;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.metrika.api.management.client.operation.OperationE;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.List;

import static java.util.stream.Collectors.toList;
import static ru.yandex.autotests.httpclient.lite.core.BackEndRequestBuilder.EMPTY_CONTEXT;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.addJsonAttachment;

/**
 * Created by okunev on 08.09.2015.
 */
public class OperationsSteps extends MetrikaBaseSteps {

    @Step("Получить список операций для счетчика {0}")
    public List<OperationE> getOperations(Long counterId) {
        return getOperations(SUCCESS_MESSAGE, expectSuccess(), counterId).getOperations();
    }

    private ManagementV1CounterCounterIdOperationsGETSchema getOperations(String message, Matcher matcher,
                                                                          Long counterId) {
        ManagementV1CounterCounterIdOperationsGETSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/operations", counterId)).get())
                .readResponse(ManagementV1CounterCounterIdOperationsGETSchema.class);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Получить операцию {1} для счетчика {0}")
    public OperationE getOperation(Long counterId, Long operationId) {
        return getOperation(SUCCESS_MESSAGE, expectSuccess(), counterId, operationId).getOperation();
    }

    @Step("Получить операцию {2} для счетчика {1} и ожидать ошибку {0}")
    public OperationE getOperationAndExpectError(IExpectedError error, Long counterId, Long operationId) {
        return getOperation(ERROR_MESSAGE, expectError(error), counterId, operationId).getOperation();
    }

    private ManagementV1CounterCounterIdOperationOperationIdGETSchema getOperation(String message, Matcher matcher,
                                                                                   Long counterId, Long operationId) {
        ManagementV1CounterCounterIdOperationOperationIdGETSchema result = this.<MetrikaJsonResponse>executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/operation/%s",
                        counterId, operationId)).get())
                .readResponse(ManagementV1CounterCounterIdOperationOperationIdGETSchema.class);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Создать операции для счетчика {0}")
    public List<OperationE> addOperations(Long counterId, List<OperationE> operations) {
        addJsonAttachment(String.format("Всего операций %s", operations.size()), JsonUtils.toString(operations));

        return operations.stream().map(operation -> addOperation(counterId, operation)).collect(toList());
    }

    @Step("Создать операцию для счетчика {0}")
    public OperationE addOperation(Long counterId, OperationE operation) {
        return addOperation(SUCCESS_MESSAGE, expectSuccess(), counterId, operation).getOperation();
    }

    @Step("Создать операцию для счетчика {1} и ожидать ошибку {0}")
    public OperationE addOperationAndExpectError(IExpectedError error, Long counterId, OperationE operation) {
        return addOperation(ERROR_MESSAGE, expectError(error), counterId, operation).getOperation();
    }

    private ManagementV1CounterCounterIdOperationsPOSTSchema addOperation(String message, Matcher matcher,
                                                                          Long counterId, OperationE operation) {
        ManagementV1CounterCounterIdOperationsPOSTSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/operations", counterId))
                        .post(new ManagementV1CounterCounterIdOperationsPOSTRequestSchema().withOperation(operation)))
                .readResponse(ManagementV1CounterCounterIdOperationsPOSTSchema.class);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Изменить операцию {1} счетчика {0}")
    public OperationE editOperation(Long counterId, Long operationId, OperationE operation) {
        return editOperation(SUCCESS_MESSAGE, expectSuccess(), counterId, operationId, operation).getOperation();
    }

    private ManagementV1CounterCounterIdOperationOperationIdPUTSchema editOperation(String message, Matcher matcher,
                                                                                    Long counterId, Long operationId,
                                                                                    OperationE operation) {
        ManagementV1CounterCounterIdOperationOperationIdPUTSchema result = this.<MetrikaJsonResponse>executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/operation/%s",
                        counterId, operationId))
                        .put(new ManagementV1CounterCounterIdOperationOperationIdPUTRequestSchema()
                                .withOperation(operation)))
                .readResponse(ManagementV1CounterCounterIdOperationOperationIdPUTSchema.class);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Удалить операции у счетчика {0}")
    public void deleteOperations(Long counterId, List<OperationE> operations) {
        addJsonAttachment(String.format("Всего операций %s", operations.size()), JsonUtils.toString(operations));

        operations.forEach(operation -> deleteOperation(counterId, operation.getId()));
    }

    @Step("Удалить операцию {1} счетчика {0}")
    public void deleteOperation(Long counterId, Long operationId) {
        if (operationId != null) {
            deleteOperation(SUCCESS_MESSAGE, expectSuccess(), counterId, operationId);
        }
    }

    private ManagementV1CounterCounterIdOperationOperationIdDELETESchema deleteOperation(String message, Matcher matcher,
                                                                                         Long counterId, Long operationId) {
        ManagementV1CounterCounterIdOperationOperationIdDELETESchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/operation/%s", counterId, operationId))
                        .delete(EMPTY_CONTEXT))
                .readResponse(ManagementV1CounterCounterIdOperationOperationIdDELETESchema.class);

        assertThat(message, result, matcher);

        return result;
    }

}
