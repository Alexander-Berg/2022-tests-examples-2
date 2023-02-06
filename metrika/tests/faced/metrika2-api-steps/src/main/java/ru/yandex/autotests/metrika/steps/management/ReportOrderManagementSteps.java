package ru.yandex.autotests.metrika.steps.management;

import java.util.Map;

import javax.annotation.Nullable;

import org.hamcrest.Matcher;
import org.joda.time.LocalDate;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.beans.schemes.InternalManagementV1CounterCounterIdReportExecutionIdGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalManagementV1CounterCounterIdReportExecutionsGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalManagementV1CounterCounterIdReportOrderIdDELETESchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalManagementV1CounterCounterIdReportOrderIdExecutionsGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalManagementV1CounterCounterIdReportOrderIdExtendPOSTSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalManagementV1CounterCounterIdReportOrderIdGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalManagementV1CounterCounterIdReportOrderIdInactivatePOSTSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalManagementV1CounterCounterIdReportOrderIdPUTSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalManagementV1CounterCounterIdReportOrderIdTokenGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalManagementV1CounterCounterIdReportOrderIdUnsubscribePOSTSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalManagementV1CounterCounterIdReportOrdersEndDatesGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalManagementV1CounterCounterIdReportOrdersGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalManagementV1CounterCounterIdReportOrdersPOSTSchema;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.autotests.metrika.utils.EmptyHttpEntity;
import ru.yandex.metrika.api.management.client.external.reportorder.*;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportExecution;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportExecutionList;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportOrder;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportOrderFrequency;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportOrderList;
import ru.yandex.metrika.util.wrappers.ReportOrderWrapper;
import ru.yandex.qatools.allure.annotations.Step;

import static ru.yandex.autotests.httpclient.lite.core.BackEndRequestBuilder.EMPTY_CONTEXT;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * @author zgmnkv
 */
public class ReportOrderManagementSteps extends MetrikaBaseSteps {

    private static final String REPORT_ORDERS_URL = "/internal/management/v1/counter/%d/report_orders";
    private static final String REPORT_ORDERS_END_DATES_URL = REPORT_ORDERS_URL + "/end_dates";

    private static final String REPORT_ORDER_URL = "/internal/management/v1/counter/%d/report_order/%d";
    private static final String REPORT_ORDER_INACTIVATE_URL = REPORT_ORDER_URL + "/inactivate";
    private static final String REPORT_ORDER_TOKEN_URL = REPORT_ORDER_URL + "/token";
    private static final String REPORT_ORDER_EXTEND_URL = REPORT_ORDER_URL + "/extend";
    private static final String REPORT_ORDER_UNSUBSCRIBE_URL = REPORT_ORDER_URL + "/unsubscribe";
    private static final String REPORT_ORDER_EXECUTIONS_URL = REPORT_ORDER_URL + "/executions";

    private static final String REPORT_EXECUTIONS_URL = "/internal/management/v1/counter/%d/report_executions";

    private static final String REPORT_EXECUTION_URL = "/internal/management/v1/counter/%d/report_execution/%d";

    @Step("Получить список заказанных отчетов для счетчика {0}")
    public ReportOrderList findReportOrders(
            Long counterId, IFormParameters... parameters
    ) {
        return findReportOrders(SUCCESS_MESSAGE, expectSuccess(), counterId, parameters);
    }

    @Step("Получить список заказанных отчетов для счетчика {1} и ожидать ошибку {0}")
    public ReportOrderList findReportOrdersAndExpectError(
            IExpectedError error, Long counterId, IFormParameters... parameters
    ) {
        return findReportOrders(ERROR_MESSAGE, expectError(error), counterId, parameters);
    }

    @Step("Создать заказанный отчет для счетчика {0}")
    public ReportOrder createReportOrder(
            Long counterId, ReportOrder reportOrder
    ) {
        return createReportOrder(SUCCESS_MESSAGE, expectSuccess(), counterId, reportOrder);
    }

    @Step("Создать заказанный отчет для счетчика {1} и ожидать ошибку {0}")
    public ReportOrder createReportOrderAndExpectError(
            IExpectedError error, Long counterId, ReportOrder reportOrder
    ) {
        return createReportOrder(ERROR_MESSAGE, expectError(error), counterId, reportOrder);
    }

    @Step("Получить даты окончаний заказанных отчетов для счетчика {0}")
    public Map<ReportOrderFrequency, LocalDate> getReportOrderEndDates(
            Long counterId
    ) {
        return getReportOrderEndDates(SUCCESS_MESSAGE, expectSuccess(), counterId);
    }

    @Step("Получить даты окончаний заказанных отчетов для счетчика {1} и ожидать ошибку {0}")
    public Map<ReportOrderFrequency, LocalDate> getReportOrderEndDatesAndExpectError(
            IExpectedError error, Long counterId
    ) {
        return getReportOrderEndDates(ERROR_MESSAGE, expectError(error), counterId);
    }

    @Step("Получить информацию о заказанном отчете {1} для счетчика {0}")
    public ReportOrder getReportOrder(
            Long counterId, Long reportOrderId
    ) {
        return getReportOrder(SUCCESS_MESSAGE, expectSuccess(), counterId, reportOrderId);
    }

    @Step("Получить информацию о заказанном отчете {2} для счетчика {1} и ожидать ошибку {0}")
    public ReportOrder getReportOrderAndExpectError(
            IExpectedError error, Long counterId, Long reportOrderId
    ) {
        return getReportOrder(ERROR_MESSAGE, expectError(error), counterId, reportOrderId);
    }

    @Step("Изменить заказанный отчет {1} для счетчика {0}")
    public ReportOrder editReportOrder(
            Long counterId, Long reportOrderId, ReportOrder reportOrder
    ) {
        return editReportOrder(SUCCESS_MESSAGE, expectSuccess(), counterId, reportOrderId, reportOrder);
    }

    @Step("Изменить заказанный отчет {2} для счетчика {1} и ожидать ошибку {0}")
    public ReportOrder editReportOrderAndExpectError(
            IExpectedError error, Long counterId, Long reportOrderId, ReportOrder reportOrder
    ) {
        return editReportOrder(ERROR_MESSAGE, expectError(error), counterId, reportOrderId, reportOrder);
    }

    @Step("Удалить заказанный отчет {1} для счетчика {0}")
    public void deleteReportOrder(
            Long counterId, Long reportOrderId
    ) {
        deleteReportOrder(SUCCESS_MESSAGE, expectSuccess(), counterId, reportOrderId);
    }

    @Step("Удалить заказанный отчет {2} для счетчика {1} и ожидать ошибку {0}")
    public void deleteReportOrderAndExpectError(
            IExpectedError error, Long counterId, Long reportOrderId
    ) {
        deleteReportOrder(ERROR_MESSAGE, expectError(error), counterId, reportOrderId);
    }

    @Step("Деактивировать заказанный отчет {1} для счетчика {0}")
    public ReportOrder inactivateReportOrder(
            Long counterId, Long reportOrderId
    ) {
        return inactivateReportOrder(SUCCESS_MESSAGE, expectSuccess(), counterId, reportOrderId);
    }

    @Step("Деактивировать заказанный отчет {2} для счетчика {1} и ожидать ошибку {0}")
    public ReportOrder inactivateReportOrderAndExpectError(
            IExpectedError error, Long counterId, Long reportOrderId
    ) {
        return inactivateReportOrder(ERROR_MESSAGE, expectError(error), counterId, reportOrderId);
    }

    @Step("Получить токен для заказанного отчета {1} для счетчика {0}")
    public String getReportOrderToken(
            Long counterId, Long reportOrderId, @Nullable String email
    ) {
        return getReportOrderToken(SUCCESS_MESSAGE, expectSuccess(), counterId, reportOrderId, email);
    }

    @Step("Получить токен для заказанного отчета {2} для счетчика {1} и ожидать ошибку {0}")
    public String getReportOrderTokenAndExpectError(
            IExpectedError error, Long counterId, Long reportOrderId, @Nullable String email
    ) {
        return getReportOrderToken(ERROR_MESSAGE, expectError(error), counterId, reportOrderId, email);
    }

    @Step("Продлить заказанный отчет {1} для счетчика {0}")
    public ReportOrder extendReportOrder(
            Long counterId, Long reportOrderId, String token
    ) {
        return extendReportOrder(SUCCESS_MESSAGE, expectSuccess(), counterId, reportOrderId, token);
    }

    @Step("Продлить заказанный отчет {2} для счетчика {1} и ожидать ошибку {0}")
    public ReportOrder extendReportOrderAndExpectError(
            IExpectedError error, Long counterId, Long reportOrderId, String token
    ) {
        return extendReportOrder(ERROR_MESSAGE, expectError(error), counterId, reportOrderId, token);
    }

    @Step("Отписаться от рассылки заказанного отчета {1} для счетчика {0} на email {2}")
    public ReportOrder unsubscribe(
            Long counterId, Long reportOrderId, String email, String token
    ) {
        return unsubscribe(SUCCESS_MESSAGE, expectSuccess(), counterId, reportOrderId, email, token);
    }

    @Step("Отписаться от рассылки заказанного отчета {2} для счетчика {1} на email {3} и ожидать ошибку {0}")
    public ReportOrder unsubscribeAndExpectError(
            IExpectedError error, Long counterId, Long reportOrderId, String email, String token
    ) {
        return unsubscribe(ERROR_MESSAGE, expectError(error), counterId, reportOrderId, email, token);
    }

    @Step("Получить список выполнений для заказанного отчета {1} для счетчика {0}")
    public ReportExecutionList findReportOrderExecutions(
            Long counterId, Long reportOrderId, IFormParameters... parameters
    ) {
        return findReportOrderExecutions(SUCCESS_MESSAGE, expectSuccess(), counterId, reportOrderId, parameters);
    }

    @Step("Получить список выполнений для заказанного отчета {2} для счетчика {1} и ожидать ошибку {0}")
    public ReportExecutionList findReportOrderExecutionsAndExpectError(
            IExpectedError error, Long counterId, Long reportOrderId, IFormParameters... parameters
    ) {
        return findReportOrderExecutions(ERROR_MESSAGE, expectError(error), counterId, reportOrderId, parameters);
    }

    @Step("Получить список выполнений отчетов для счетчика {0}")
    public ReportExecutionList findReportExecutions(
            Long counterId, IFormParameters... parameters
    ) {
        return findReportExecutions(SUCCESS_MESSAGE, expectSuccess(), counterId, parameters);
    }

    @Step("Получить список выполнений отчетов для счетчика {1} и ожидать ошибку {0}")
    public ReportExecutionList findReportExecutionsAndExpectError(
            IExpectedError error, Long counterId, IFormParameters... parameters
    ) {
        return findReportExecutions(ERROR_MESSAGE, expectError(error), counterId, parameters);
    }

    @Step("Получить информацию о выполнении отчета {1} для счетчика {0}")
    public ReportExecution getReportExecution(
            Long counterId, Long reportExecutionId
    ) {
        return getReportExecution(SUCCESS_MESSAGE, expectSuccess(), counterId, reportExecutionId);
    }

    @Step("Получить информацию о выполнении отчета {2} для счетчика {1} и ожидать ошибку {0}")
    public ReportExecution getReportExecutionAndExpectError(
            IExpectedError error, Long counterId, Long reportExecutionId
    ) {
        return getReportExecution(ERROR_MESSAGE, expectError(error), counterId, reportExecutionId);
    }

    private ReportOrderList findReportOrders(
            String message, Matcher matcher, Long counterId, IFormParameters... parameters
    ) {
        InternalManagementV1CounterCounterIdReportOrdersGETSchema result = executeAsJson(
                getRequestBuilder(String.format(REPORT_ORDERS_URL, counterId))
                        .get(parameters)
        ).readResponse(InternalManagementV1CounterCounterIdReportOrdersGETSchema.class);

        assertThat(message, result, matcher);

        return result.getReportOrders();
    }

    private ReportOrder createReportOrder(
            String message, Matcher matcher, Long counterId, ReportOrder reportOrder
    ) {
        InternalManagementV1CounterCounterIdReportOrdersPOSTSchema result = executeAsJson(
                getRequestBuilder(String.format(REPORT_ORDERS_URL, counterId)).post(
                        new ReportOrderWrapper().withReportOrder(reportOrder)
                )
        ).readResponse(InternalManagementV1CounterCounterIdReportOrdersPOSTSchema.class);

        assertThat(message, result, matcher);

        return result.getReportOrder();
    }

    private Map<ReportOrderFrequency, LocalDate> getReportOrderEndDates(
            String message, Matcher matcher, Long counterId
    ) {
        InternalManagementV1CounterCounterIdReportOrdersEndDatesGETSchema result = executeAsJson(
                getRequestBuilder(String.format(REPORT_ORDERS_END_DATES_URL, counterId))
                        .get()
        ).readResponse(InternalManagementV1CounterCounterIdReportOrdersEndDatesGETSchema.class);

        assertThat(message, result, matcher);

        return result.getEndDates();
    }

    private ReportOrder getReportOrder(
            String message, Matcher matcher, Long counterId, Long reportOrderId
    ) {
        InternalManagementV1CounterCounterIdReportOrderIdGETSchema result = executeAsJson(
                getRequestBuilder(String.format(REPORT_ORDER_URL, counterId, reportOrderId))
                        .get()
        ).readResponse(InternalManagementV1CounterCounterIdReportOrderIdGETSchema.class);

        assertThat(message, result, matcher);

        return result.getReportOrder();
    }

    private ReportOrder editReportOrder(
            String message, Matcher matcher, Long counterId, Long reportOrderId, ReportOrder reportOrder
    ) {
        InternalManagementV1CounterCounterIdReportOrderIdPUTSchema result = executeAsJson(
                getRequestBuilder(String.format(REPORT_ORDER_URL, counterId, reportOrderId))
                        .put(new ReportOrderWrapper().withReportOrder(reportOrder))
        ).readResponse(InternalManagementV1CounterCounterIdReportOrderIdPUTSchema.class);

        assertThat(message, result, matcher);

        return result.getReportOrder();
    }

    private void deleteReportOrder(
            String message, Matcher matcher, Long counterId, Long reportOrderId
    ) {
        InternalManagementV1CounterCounterIdReportOrderIdDELETESchema result = executeAsJson(
                getRequestBuilder(String.format(REPORT_ORDER_URL, counterId, reportOrderId))
                        .delete(EMPTY_CONTEXT)
        ).readResponse(InternalManagementV1CounterCounterIdReportOrderIdDELETESchema.class);

        assertThat(message, result, matcher);
    }

    private ReportOrder inactivateReportOrder(
            String message, Matcher matcher, Long counterId, Long reportOrderId
    ) {
        InternalManagementV1CounterCounterIdReportOrderIdInactivatePOSTSchema result = executeAsJson(
                getRequestBuilder(String.format(REPORT_ORDER_INACTIVATE_URL, counterId, reportOrderId))
                        .post(new EmptyHttpEntity(), EMPTY_CONTEXT)
        ).readResponse(InternalManagementV1CounterCounterIdReportOrderIdInactivatePOSTSchema.class);

        assertThat(message, result, matcher);

        return result.getReportOrder();
    }

    private String getReportOrderToken(
            String message, Matcher matcher, Long counterId, Long reportOrderId, @Nullable String email
    ) {
        InternalManagementV1CounterCounterIdReportOrderIdTokenGETSchema result = executeAsJson(
                getRequestBuilder(String.format(REPORT_ORDER_TOKEN_URL, counterId, reportOrderId))
                        .get(FreeFormParameters.makeParameters()
                                .append("email", email)
                        )
        ).readResponse(InternalManagementV1CounterCounterIdReportOrderIdTokenGETSchema.class);

        assertThat(message, result, matcher);

        return result.getToken();
    }

    private ReportOrder extendReportOrder(
            String message, Matcher matcher, Long counterId, Long reportOrderId, String token
    ) {
        InternalManagementV1CounterCounterIdReportOrderIdExtendPOSTSchema result = executeAsJson(
                getRequestBuilder(String.format(REPORT_ORDER_EXTEND_URL, counterId, reportOrderId))
                        .post(new EmptyHttpEntity(), FreeFormParameters.makeParameters()
                                .append("token", token)
                        )
        ).readResponse(InternalManagementV1CounterCounterIdReportOrderIdExtendPOSTSchema.class);

        assertThat(message, result, matcher);

        return result.getReportOrder();
    }

    private ReportOrder unsubscribe(
            String message, Matcher matcher, Long counterId, Long reportOrderId, String email, String token
    ) {
        InternalManagementV1CounterCounterIdReportOrderIdUnsubscribePOSTSchema result = executeAsJson(
                getRequestBuilder(String.format(REPORT_ORDER_UNSUBSCRIBE_URL, counterId, reportOrderId))
                        .post(new EmptyHttpEntity(), FreeFormParameters.makeParameters()
                                .append("email", email)
                                .append("token", token)
                        )
        ).readResponse(InternalManagementV1CounterCounterIdReportOrderIdUnsubscribePOSTSchema.class);

        assertThat(message, result, matcher);

        return result.getReportOrder();
    }

    private ReportExecutionList findReportOrderExecutions(
            String message, Matcher matcher, Long counterId, Long reportOrderId, IFormParameters... parameters
    ) {
        InternalManagementV1CounterCounterIdReportOrderIdExecutionsGETSchema result = executeAsJson(
                getRequestBuilder(String.format(REPORT_ORDER_EXECUTIONS_URL, counterId, reportOrderId))
                        .get(parameters)
        ).readResponse(InternalManagementV1CounterCounterIdReportOrderIdExecutionsGETSchema.class);

        assertThat(message, result, matcher);

        return result.getReportExecutions();
    }

    private ReportExecutionList findReportExecutions(
            String message, Matcher matcher, Long counterId, IFormParameters... parameters
    ) {
        InternalManagementV1CounterCounterIdReportExecutionsGETSchema result = executeAsJson(
                getRequestBuilder(String.format(REPORT_EXECUTIONS_URL, counterId))
                        .get(parameters)
        ).readResponse(InternalManagementV1CounterCounterIdReportExecutionsGETSchema.class);

        assertThat(message, result, matcher);

        return result.getReportExecutions();
    }

    private ReportExecution getReportExecution(
            String message, Matcher matcher, Long counterId, Long reportExecutionId
    ) {
        InternalManagementV1CounterCounterIdReportExecutionIdGETSchema result = executeAsJson(
                getRequestBuilder(String.format(REPORT_EXECUTION_URL, counterId, reportExecutionId))
                        .get()
        ).readResponse(InternalManagementV1CounterCounterIdReportExecutionIdGETSchema.class);

        assertThat(message, result, matcher);

        return result.getReportExecution();
    }
}
