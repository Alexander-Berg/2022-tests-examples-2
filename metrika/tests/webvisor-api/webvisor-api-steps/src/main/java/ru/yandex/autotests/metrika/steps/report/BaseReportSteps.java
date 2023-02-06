package ru.yandex.autotests.metrika.steps.report;

import org.hamcrest.Matcher;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.irt.testutils.allure.TestSteps;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataCsvSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataXlsxSchema;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.report.v1.enums.FormatEnum;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.qatools.allure.annotations.Step;

import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;


/**
 * Created by konkov on 02.12.2014.
 * <p>
 * Базовый класс для степов работы с отчетами
 */
public abstract class BaseReportSteps extends MetrikaBaseSteps {

    @Step("Построить сырой отчет {0}")
    public Object getRawReport(RequestType<?> method, IFormParameters... parameters) {
        return getJsonReport(method, parameters);
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
     * Получить отчет от сервиса в формате csv и ожидать успеха
     *
     * @param requestType тип запроса
     * @param parameters  параметры запроса
     * @return результат запроса
     */
    protected StatV1DataCsvSchema getCsvReportAndExpectSuccess(RequestType<?> requestType, IFormParameters...
            parameters) {
        String csvPath = requestType.getPath().concat(FormatEnum.CSV.getFormat());

        StatV1DataCsvSchema report = executeAsCsv(getRequestBuilder(csvPath).get(parameters)).readResponse();

        TestSteps.assertThat(SUCCESS_MESSAGE, report, expectSuccess());

        return report;
    }

    /**
     * Получить отчет от сервиса в формате xlsx и ожидать успеха
     *
     * @param requestType тип запроса
     * @param parameters  параметры запроса
     * @return результат запроса
     */
    protected StatV1DataXlsxSchema getXlsxReportAndExpectSuccess(RequestType<?> requestType, IFormParameters...
            parameters) {
        String xlsxPath = requestType.getPath().concat(FormatEnum.XLSX.getFormat());

        StatV1DataXlsxSchema report = executeAsXlsx(getRequestBuilder(xlsxPath).get(parameters)).readResponse();

        TestSteps.assertThat(SUCCESS_MESSAGE, report, expectSuccess());

        return report;
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
    private <T> T getJsonReportAndCheckResult(RequestType<T> requestType, String message,
                                              Matcher matcher, IFormParameters... parameters) {
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
    protected <T> T getJsonReportAndExpectError(RequestType<T> requestType, IExpectedError expectedError,
                                                IFormParameters... parameters) {
        return getJsonReportAndCheckResult(requestType, ERROR_MESSAGE, expectError(expectedError), parameters);
    }
}
