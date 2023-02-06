package ru.yandex.autotests.metrika.steps.report;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.beans.schemes.*;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.qatools.allure.annotations.Step;

import static ru.yandex.autotests.metrika.errors.CustomError.expect;

/**
 * Created by okunev on 21.10.2014.
 */
public class LegacyReportSteps extends BaseReportSteps {

    @Step("Построить отчет предыдущей версии 'таблица'")
    public StatV1DataGETSchema getTableReportAndExpectSuccess(IFormParameters... parameters) {
        return getJsonReportAndExpectSuccess(RequestTypes.LEGACY_TABLE,
                parameters);
    }

    @Step("Построить отчет предыдущей версии 'таблица' и ожидать ошибки {0} {1}")
    public StatV1DataGETSchema getTableReportAndExpectError(Long code, String message, IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.LEGACY_TABLE, expect(code, message), parameters);
    }

    @Step("Построить отчет предыдущей версии в формате csv")
    public StatV1DataCsvSchema getCsvReportAndExpectSuccess(IFormParameters... parameters) {
        return getCsvReportAndExpectSuccess(RequestTypes.LEGACY_TABLE, parameters);
    }

    @Step("Построить отчет предыдущей версии в формате xlsx")
    public StatV1DataXlsxSchema getXlsxReportAndExpectSuccess(IFormParameters... parameters) {
        return getXlsxReportAndExpectSuccess(RequestTypes.LEGACY_TABLE, parameters);
    }

    @Step("Построить отчет предыдущей версии 'по времени'")
    public StatV1DataBytimeGETSchema getBytimeReportAndExpectSuccess(IFormParameters... parameters) {
        return getJsonReportAndExpectSuccess(RequestTypes.LEGACY_BY_TIME, parameters);
    }

    @Step("Построить отчет предыдущей версии 'по времени' и ожидать ошибки {0} {1}")
    public StatV1DataBytimeGETSchema getBytimeReportAndExpectError(Long code, String message,
                                                                   IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.LEGACY_BY_TIME, expect(code, message), parameters);
    }

}
