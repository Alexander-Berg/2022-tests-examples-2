package ru.yandex.autotests.metrika.steps.report;

import org.apache.commons.lang3.ArrayUtils;
import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.beans.schemes.*;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.reportwrappers.Report;
import ru.yandex.autotests.metrika.reportwrappers.ReportFactory;
import ru.yandex.qatools.allure.annotations.Step;

import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.errors.CustomError.expect;

/**
 * Created by okunev on 21.10.2014.
 */
public class ReportSteps extends BaseReportSteps {

    @Step("Построить отчет {0}")
    public Report getReportAndExpectSuccess(RequestType<?> method, IFormParameters... parameters) {
        return ReportFactory.create(method.getResponseClass(), getJsonReportAndExpectSuccess(method, parameters));
    }

    @Step("Построить отчет {0} и ожидать ошибку {1}")
    public Report getReportAndExpectError(RequestType<?> method, IExpectedError error, IFormParameters... parameters) {
        return ReportFactory.create(method.getResponseClass(), getJsonReportAndExpectError(method, error, parameters));
    }

    @Step("Построить отчет 'таблица'")
    public StatV1DataGETSchema getTableReportAndExpectSuccess(IFormParameters... parameters) {
        return getJsonReportAndExpectSuccess(RequestTypes.TABLE, parameters);
    }

    @Step("Построить отчет 'таблица' и ожидать ошибки {0} {1}")
    public StatV1DataGETSchema getTableReportAndExpectError(Long code, String message, IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.TABLE, expect(code, message), parameters);
    }

    @Step("Построить отчет 'таблица' и ожидать ошибки {0} {1}")
    public StatV1DataGETSchema getTableReportAndExpectError(Long code, Matcher<String> message,
                                                            IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.TABLE, expect(code, message), parameters);
    }

    public StatV1DataGETSchema getTableReportAndExpectError(IExpectedError error,
                                                            IFormParameters... parameters) {
        return getTableReportAndExpectError(error.getCode(), error.getMessage(), parameters);
    }

    @Step("Построить отчет 'таблица' с callback'ом")
    public String getTableReport(String callback, IFormParameters... parameters) {
        return executeAsJavaScript(getRequestBuilder(RequestTypes.TABLE.getPath())
                .get(ArrayUtils.add(parameters, makeParameters("callback", callback)))).readResponse();
    }

    @Step("Построить отчет 'Список заказов и товаров'")
    public StatV1DataGETSchema getEcommerceOrdersTableReportAndExpectSuccess(IFormParameters... parameters) {
        return getJsonReportAndExpectSuccess(RequestTypes.ECOMMERCE_ORDERS_TABLE, parameters);
    }

    @Step("Построить отчет 'по времени'")
    public StatV1DataBytimeGETSchema getBytimeReportAndExpectSuccess(IFormParameters... parameters) {
        return getJsonReportAndExpectSuccess(RequestTypes.BY_TIME, parameters);
    }

    @Step("Построить отчет 'по времени' и ожидать ошибки {0} {1}")
    public StatV1DataBytimeGETSchema getBytimeReportAndExpectError(Long code, String message,
                                                                   IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.BY_TIME, expect(code, message), parameters);
    }

    @Step("Построить отчет 'по времени' и ожидать ошибки {0} {1}")
    public StatV1DataBytimeGETSchema getBytimeReportAndExpectError(Long code, Matcher<String> message,
                                                                   IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.BY_TIME, expect(code, message), parameters);
    }

    public StatV1DataBytimeGETSchema getBytimeReportAndExpectError(IExpectedError error,
                                                                   IFormParameters... parameters) {
        return getBytimeReportAndExpectError(error.getCode(), error.getMessage(), parameters);
    }

    @Step("Построить отчет 'Drill down'")
    public StatV1DataDrilldownGETSchema getDrilldownReportAndExpectSuccess(IFormParameters... parameters) {
        return getJsonReportAndExpectSuccess(RequestTypes.DRILLDOWN, parameters);
    }

    @Step("Построить отчет 'Drill down' и ожидать ошибки {0} {1}")
    public StatV1DataDrilldownGETSchema getDrilldownReportAndExpectError(Long code, String message,
                                                                         IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.DRILLDOWN, expect(code, message), parameters);
    }

    @Step("Построить отчет 'Drill down' и ожидать ошибки {0} {1}")
    public StatV1DataDrilldownGETSchema getDrilldownReportAndExpectError(Long code, Matcher<String> message,
                                                                         IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.DRILLDOWN, expect(code, message), parameters);
    }

    @Step("Построить отчет 'Drill down - список заказов и товаров'")
    public StatV1DataDrilldownGETSchema getEcommerceOrdersDrilldownReportAndExpectSuccess(IFormParameters... parameters) {
        return getJsonReportAndExpectSuccess(RequestTypes.ECOMMERCE_ORDERS_DRILLDOWN, parameters);
    }

    public StatV1DataDrilldownGETSchema getDrilldownReportAndExpectError(IExpectedError error,
                                                                         IFormParameters... parameters) {
        return getDrilldownReportAndExpectError(error.getCode(), error.getMessage(), parameters);
    }

    @Step("Построить отчет 'сравнение сегментов'")
    public StatV1DataComparisonGETSchema getComparisonReportAndExpectSuccess(IFormParameters... parameters) {
        return getJsonReportAndExpectSuccess(RequestTypes.COMPARISON, parameters);
    }

    @Step("Построить отчет 'сравнение сегментов' и ожидать ошибки {0} {1}")
    public StatV1DataComparisonGETSchema getComparisonReportAndExpectError(Long code, String message,
                                                                           IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.COMPARISON, expect(code, message), parameters);
    }

    @Step("Построить отчет 'сравнение сегментов' и ожидать ошибки {0} {1}")
    public StatV1DataComparisonGETSchema getComparisonReportAndExpectError(Long code, Matcher<String> message,
                                                                           IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.COMPARISON, expect(code, message), parameters);
    }

    public StatV1DataComparisonGETSchema getComparisonReportAndExpectError(IExpectedError error,
                                                                           IFormParameters... parameters) {
        return getComparisonReportAndExpectError(error.getCode(), error.getMessage(), parameters);
    }

    @Step("Построить отчет 'сравнение - drill down'")
    public StatV1DataComparisonDrilldownGETSchema getComparisonDrilldownReportAndExpectSuccess(
            IFormParameters... parameters) {
        return getJsonReportAndExpectSuccess(RequestTypes.COMPARISON_DRILLDOWN, parameters);
    }

    @Step("Построить отчет 'сравнение - drill down' и ожидать ошибки {0} {1}")
    public StatV1DataComparisonDrilldownGETSchema getComparisonDrilldownReportAndExpectError(
            Long code, String message,
            IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.COMPARISON_DRILLDOWN, expect(code, message), parameters);
    }

    @Step("Построить отчет 'сравнение - drill down' и ожидать ошибки {0} {1}")
    public StatV1DataComparisonDrilldownGETSchema getComparisonDrilldownReportAndExpectError(
            Long code, Matcher<String> message,
            IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.COMPARISON_DRILLDOWN, expect(code, message), parameters);
    }

    public StatV1DataComparisonDrilldownGETSchema getComparisonDrilldownReportAndExpectError(
            IExpectedError error,
            IFormParameters... parameters) {
        return getComparisonDrilldownReportAndExpectError(error.getCode(), error.getMessage(), parameters);
    }

    @Step("Построить отчет 'google analytics'")
    public AnalyticsV3DataGaGETSchema getAnalyticsReportAndExpectSuccess(IFormParameters... parameters) {
        return getAnalyticsReportAndCheckResult(SUCCESS_MESSAGE, expectSuccess(), parameters);
    }

    @Step("Построить отчет 'google analytics' и ожидать ошибку {0}")
    public AnalyticsV3DataGaGETSchema getAnalyticsReportAndExpectError(IExpectedError error,
                                                                       IFormParameters... parameters) {
        return getAnalyticsReportAndCheckResult(ERROR_MESSAGE, expectError(error), parameters);
    }

    @Step("Построить отчет csv {0}")
    public StatV1DataCsvSchema getCsvReport(RequestType<?> method, IFormParameters... parameterses) {
        return getCsvReportAndExpectSuccess(method, parameterses);
    }

    @Step("Построить отчет xlsx {0}")
    public StatV1DataXlsxSchema getXlsxReport(RequestType<?> method, IFormParameters... parameterses) {
        return getXlsxReportAndExpectSuccess(method, parameterses);
    }

    @Step("Построить отчет в формате csv")
    public StatV1DataCsvSchema getCsvReportAndExpectSuccess(IFormParameters... parameters) {
        return getCsvReportAndExpectSuccess(RequestTypes.TABLE, parameters);
    }

    @Step("Построить отчет в формате xlsx")
    public StatV1DataXlsxSchema getXlsxReportAndExpectSuccess(IFormParameters... parameters) {
        return getXlsxReportAndExpectSuccess(RequestTypes.TABLE, parameters);
    }

    @Step("Построить отчет 'сравнение сегментов' в формате csv")
    public StatV1DataCsvSchema getCsvComparisonReportAndExpectSuccess(IFormParameters... parameters) {
        return getCsvReportAndExpectSuccess(RequestTypes.COMPARISON, parameters);
    }

    @Step("Построить отчет 'сравнение сегментов' в формате xlsx")
    public StatV1DataXlsxSchema getXlsxComparisonReportAndExpectSuccess(IFormParameters... parameters) {
        return getXlsxReportAndExpectSuccess(RequestTypes.COMPARISON, parameters);
    }

    @Step("Построить отчет 'Заказы и товары' в формате csv")
    public StatV1DataCsvSchema getCsvEcommerceOrdersReportAndExpectSuccess(IFormParameters... parameters) {
        return getCsvReportAndExpectSuccess(RequestTypes.ECOMMERCE_ORDERS_TABLE, parameters);
    }

    @Step("Построить отчет 'Заказы и товары' в формате xlsx")
    public StatV1DataXlsxSchema getXlsxEcommerceOrdersReportAndExpectSuccess(IFormParameters... parameters) {
        return getXlsxReportAndExpectSuccess(RequestTypes.ECOMMERCE_ORDERS_TABLE, parameters);
    }

    @Step("Построить отчет 'Конверсии' в формате csv")
    public StatV1DataCsvSchema getCsvConversionRateReportAndExpectSuccess(IFormParameters... parameterses) {
        return getCsvReportAndExpectSuccess(RequestTypes.CONVERSION_RATE, parameterses);
    }

    @Step("Построить отчет 'Конверсии' в формате xlsx")
    public StatV1DataXlsxSchema getXlsxConversionRateReportAndExpectSuccess(IFormParameters... parameterses) {
        return getXlsxReportAndExpectSuccess(RequestTypes.CONVERSION_RATE, parameterses);
    }

    @Step("Построить отчет 'по времени'  в формате csv")
    public StatV1DataCsvSchema getBytimeCsvReportAndExpectSuccess(IFormParameters... parameters) {
        return getCsvReportAndExpectSuccess(RequestTypes.BY_TIME, parameters);
    }

    @Step("Построить отчет 'по времени' в формате xlsx")
    public StatV1DataXlsxSchema getBytimeXlsxReportAndExpectSuccess(IFormParameters... parameters) {
        return getXlsxReportAndExpectSuccess(RequestTypes.BY_TIME, parameters);
    }

    @Step("Получить лог мониторинга")
    public StatV1CustomMonitoringLogGETSchema getMonitoringLogAndExpectSuccess(IFormParameters... parameters) {
        return getJsonReportAndExpectSuccess(RequestTypes.MONITORING_LOG, parameters);
    }

    @Step("Получить лог мониторинга и ожидать ошибку {0}")
    public StatV1CustomMonitoringLogGETSchema getMonitoringLogAndExpectError(IExpectedError error, IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.MONITORING_LOG, error, parameters);
    }

    @Step("Получить количество http и https визитов")
    public StatV1DataVisitsByProtocolGETSchema getVisitsByProtocolAndExpectSuccess(IFormParameters... parameters) {
        return getJsonReportAndExpectSuccess(RequestTypes.VISITS_BY_PROTOCOL, parameters);
    }
}
