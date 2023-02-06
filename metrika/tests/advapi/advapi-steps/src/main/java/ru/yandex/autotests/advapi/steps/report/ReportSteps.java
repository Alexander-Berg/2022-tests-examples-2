package ru.yandex.autotests.advapi.steps.report;

import org.hamcrest.Matcher;
import ru.yandex.advapi.V1StatDataBytimeGETSchema;
import ru.yandex.advapi.V1StatDataDrilldownGETSchema;
import ru.yandex.advapi.V1StatDataGETSchema;
import ru.yandex.autotests.advapi.data.common.RequestType;
import ru.yandex.autotests.advapi.data.common.RequestTypes;
import ru.yandex.autotests.advapi.reportwrappers.Report;
import ru.yandex.autotests.advapi.reportwrappers.ReportFactory;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.irt.testutils.allure.TestSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.qatools.allure.annotations.Step;

import static ru.yandex.autotests.metrika.commons.response.CustomError.expect;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;

/**
 * Created by okunev on 21.10.2014.
 */
public class ReportSteps extends BaseReportSteps {

    @Step("Построить сырой отчет {0}")
    public Object getRawReport(RequestType<?> method, IFormParameters... parameters) {
        return getJsonReport(method, parameters);
    }

    @Step("Построить отчет {0}")
    public Report getReportAndExpectSuccess(RequestType<?> method, IFormParameters... parameters) {
        return ReportFactory.create(method.getResponseClass(), getJsonReportAndExpectSuccess(method, parameters));
    }

    @Step("Построить отчет {0} и ожидать ошибку {1}")
    public Report getReportAndExpectError(RequestType<?> method, IExpectedError error, IFormParameters... parameters) {
        return ReportFactory.create(method.getResponseClass(), getJsonReportAndExpectError(method, error, parameters));
    }

    @Step("Построить отчет 'таблица'")
    public V1StatDataGETSchema getTableReportAndExpectSuccess(IFormParameters... parameters) {
        return getJsonReportAndExpectSuccess(RequestTypes.TABLE, parameters);
    }

    @Step("Построить отчет 'таблица' и ожидать ошибки {0} {1}")
    public V1StatDataGETSchema getTableReportAndExpectError(Long code, String message, IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.TABLE, expect(code, message), parameters);
    }

    @Step("Построить отчет 'таблица' и ожидать ошибки {0} {1}")
    public V1StatDataGETSchema getTableReportAndExpectError(Long code, Matcher<String> message, IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.TABLE, expect(code, message), parameters);
    }

    public V1StatDataGETSchema getTableReportAndExpectError(IExpectedError error, IFormParameters... parameters) {
        return getTableReportAndExpectError(error.getCode(), error.getMessage(), parameters);
    }

    @Step("Построить отчет 'по времени'")
    public V1StatDataBytimeGETSchema getBytimeReportAndExpectSuccess(IFormParameters... parameters) {
        return getJsonReportAndExpectSuccess(RequestTypes.BY_TIME, parameters);
    }

    @Step("Построить отчет 'по времени' и ожидать ошибки {0} {1}")
    public V1StatDataBytimeGETSchema getBytimeReportAndExpectError(Long code, String message, IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.BY_TIME, expect(code, message), parameters);
    }

    @Step("Построить отчет 'по времени' и ожидать ошибки {0} {1}")
    public V1StatDataBytimeGETSchema getBytimeReportAndExpectError(Long code, Matcher<String> message, IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.BY_TIME, expect(code, message), parameters);
    }

    public V1StatDataBytimeGETSchema getBytimeReportAndExpectError(IExpectedError error, IFormParameters... parameters) {
        return getBytimeReportAndExpectError(error.getCode(), error.getMessage(), parameters);
    }

    @Step("Построить отчет 'Drill down'")
    public V1StatDataDrilldownGETSchema getDrilldownReportAndExpectSuccess(IFormParameters... parameters) {
        return getJsonReportAndExpectSuccess(RequestTypes.DRILLDOWN, parameters);
    }

    @Step("Построить отчет 'Drill down' и ожидать ошибки {0} {1}")
    public V1StatDataDrilldownGETSchema getDrilldownReportAndExpectError(Long code, String message, IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.DRILLDOWN, expect(code, message), parameters);
    }

    @Step("Построить отчет 'Drill down' и ожидать ошибки {0} {1}")
    public V1StatDataDrilldownGETSchema getDrilldownReportAndExpectError(Long code, Matcher<String> message, IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.DRILLDOWN, expect(code, message), parameters);
    }

    public V1StatDataDrilldownGETSchema getDrilldownReportAndExpectError(IExpectedError error, IFormParameters... parameters) {
        return getDrilldownReportAndExpectError(error.getCode(), error.getMessage(), parameters);
    }

    /**
     * Получить отчет от сервиса в формате json
     *
     * @param requestType тип запроса
     * @param parameters  параметры запроса
     * @param <T>         тип результата
     * @return результат запроса
     */
    private <T> T getJsonReport(RequestType<T> requestType, IFormParameters... parameters) {
        return executeWithSemaphore(() ->
                getResponse(requestType.getPath(), parameters).readResponse(requestType.getResponseClass()));
    }

    /**
     * Получить отчет от сервиса и проверить результат
     *
     * @param requestType тип запроса
     * @param message     сообщение
     * @param matcher     матчер для проверки
     * @param parameters  параметры запроса
     * @param <T>         тип результата
     * @return результат запроса
     */
    private <T> T getJsonReportAndCheckResult(RequestType<T> requestType, String message, Matcher matcher, IFormParameters... parameters) {
        T report = getJsonReport(requestType, parameters);
        TestSteps.assertThat(message, report, matcher);
        return report;
    }

    /**
     * Получить отчет и ожидать успеха
     *
     * @param requestType тип запроса
     * @param parameters  параметры запроса
     * @param <T>         тип результата
     * @return результат запроса
     */
    protected <T> T getJsonReportAndExpectSuccess(RequestType<T> requestType, IFormParameters... parameters) {
        return getJsonReportAndCheckResult(requestType, SUCCESS_MESSAGE, expectSuccess(), parameters);
    }

    /**
     * Получить отчет и ождать ошибки
     *
     * @param requestType   тип запроса
     * @param expectedError ожидаемая ошибка
     * @param parameters    параметры запроса
     * @param <T>           тип результата
     * @return результат запроса
     */
    protected <T> T getJsonReportAndExpectError(RequestType<T> requestType, IExpectedError expectedError, IFormParameters... parameters) {
        return getJsonReportAndCheckResult(requestType, ERROR_MESSAGE, expectError(expectedError), parameters);
    }
}
