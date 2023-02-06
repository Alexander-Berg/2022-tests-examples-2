package ru.yandex.autotests.metrika.steps.report;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.beans.schemes.InternalStatV1CounterCounterIdReportExecutionReportExecutionIdDataBytimeGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalStatV1CounterCounterIdReportExecutionReportExecutionIdDataGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataCsvSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataXlsxSchema;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.report.v1.enums.FormatEnum;
import ru.yandex.qatools.allure.annotations.Step;

import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * @author zgmnkv
 */
public class ReportOrderStatSteps extends BaseReportSteps {

    private static final String TABLE_REPORT_URL = "/internal/stat/v1/counter/%d/report_execution/%d/data";
    private static final String BY_TIME_REPORT_URL = "/internal/stat/v1/counter/%d/report_execution/%d/data/bytime";

    @Step("Получить построенный заказанный отчет {1} для счетчика {0}")
    public InternalStatV1CounterCounterIdReportExecutionReportExecutionIdDataGETSchema getTableReport(
            Long counterId, Long reportExecutionId, IFormParameters... parameters
    ) {
        return getReport(
                InternalStatV1CounterCounterIdReportExecutionReportExecutionIdDataGETSchema.class, TABLE_REPORT_URL,
                SUCCESS_MESSAGE, expectSuccess(),
                counterId, reportExecutionId, parameters
        );
    }

    @Step("Получить построенный заказанный отчет {2} для счетчика {1} и ожидать ошибку {0}")
    public InternalStatV1CounterCounterIdReportExecutionReportExecutionIdDataGETSchema getTableReportAndExpectError(
            IExpectedError error, Long counterId, Long reportExecutionId, IFormParameters... parameters
    ) {
        return getReport(
                InternalStatV1CounterCounterIdReportExecutionReportExecutionIdDataGETSchema.class, TABLE_REPORT_URL,
                ERROR_MESSAGE, expectError(error),
                counterId, reportExecutionId, parameters
        );
    }

    @Step("Получить построенный заказанный отчет {1} для счетчика {0} в формате csv")
    public StatV1DataCsvSchema getCsvTableReport(
            Long counterId, Long reportExecutionId, IFormParameters... parameters
    ) {
        return getCsvReport(
                TABLE_REPORT_URL,
                SUCCESS_MESSAGE, expectSuccess(),
                counterId, reportExecutionId, parameters
        );
    }

    @Step("Получить построенный заказанный отчет {1} для счетчика {0} в формате xlsx")
    public StatV1DataXlsxSchema getXlsxTableReport(
            Long counterId, Long reportExecutionId, IFormParameters... parameters
    ) {
        return getXlsxReport(
                TABLE_REPORT_URL,
                SUCCESS_MESSAGE, expectSuccess(),
                counterId, reportExecutionId, parameters
        );
    }

    @Step("Получить построенный заказанный отчет {1} по времени для счетчика {0}")
    public InternalStatV1CounterCounterIdReportExecutionReportExecutionIdDataBytimeGETSchema getByTimeReport(
            Long counterId, Long reportExecutionId, IFormParameters... parameters
    ) {
        return getReport(
                InternalStatV1CounterCounterIdReportExecutionReportExecutionIdDataBytimeGETSchema.class, BY_TIME_REPORT_URL,
                SUCCESS_MESSAGE, expectSuccess(),
                counterId, reportExecutionId, parameters
        );
    }

    @Step("Получить построенный заказанный отчет {2} по времени для счетчика {1} и ожидать ошибку {0}")
    public InternalStatV1CounterCounterIdReportExecutionReportExecutionIdDataBytimeGETSchema getByTimeReportAndExpectError(
            IExpectedError error, Long counterId, Long reportExecutionId, IFormParameters... parameters
    ) {
        return getReport(
                InternalStatV1CounterCounterIdReportExecutionReportExecutionIdDataBytimeGETSchema.class, BY_TIME_REPORT_URL,
                ERROR_MESSAGE, expectError(error),
                counterId, reportExecutionId, parameters
        );
    }

    @Step("Получить построенный заказанный отчет {1} по времени для счетчика {0} в формате csv")
    public StatV1DataCsvSchema getCsvByTimeReport(
            Long counterId, Long reportExecutionId, IFormParameters... parameters
    ) {
        return getCsvReport(
                BY_TIME_REPORT_URL,
                SUCCESS_MESSAGE, expectSuccess(),
                counterId, reportExecutionId, parameters
        );
    }

    @Step("Получить построенный заказанный отчет {1} по времени для счетчика {0} в формате xlsx")
    public StatV1DataXlsxSchema getXlsxByTimeReport(
            Long counterId, Long reportExecutionId, IFormParameters... parameters
    ) {
        return getXlsxReport(
                BY_TIME_REPORT_URL,
                SUCCESS_MESSAGE, expectSuccess(),
                counterId, reportExecutionId, parameters
        );
    }

    private <T> T getReport(
            Class<T> responseClass, String url,
            String message, Matcher matcher,
            Long counterId, Long reportExecutionId, IFormParameters... parameters
    ) {
        T result = getResponse(
                String.format(url, counterId, reportExecutionId), parameters
        ).readResponse(responseClass);

        assertThat(message, result, matcher);

        return result;
    }

    private StatV1DataCsvSchema getCsvReport(
            String baseUrl,
            String message, Matcher matcher,
            Long counterId, Long reportExecutionId, IFormParameters... parameters
    ) {
        String url = baseUrl.concat(FormatEnum.CSV.getFormat());

        StatV1DataCsvSchema result = executeAsCsv(
                getRequestBuilder(String.format(url, counterId, reportExecutionId))
                        .get(parameters)
        ).readResponse();

        assertThat(message, result, matcher);

        return result;
    }

    private StatV1DataXlsxSchema getXlsxReport(
            String baseUrl,
            String message, Matcher matcher,
            Long counterId, Long reportExecutionId, IFormParameters... parameters
    ) {
        String url = baseUrl.concat(FormatEnum.XLSX.getFormat());

        StatV1DataXlsxSchema result = executeAsXlsx(
                getRequestBuilder(String.format(url, counterId, reportExecutionId))
                        .get(parameters)
        ).readResponse();

        assertThat(message, result, matcher);

        return result;
    }
}
