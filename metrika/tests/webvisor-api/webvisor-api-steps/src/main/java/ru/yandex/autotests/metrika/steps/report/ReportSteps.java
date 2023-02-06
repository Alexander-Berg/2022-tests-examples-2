package ru.yandex.autotests.metrika.steps.report;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataCsvSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataXlsxSchema;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.qatools.allure.annotations.Step;

/**
 * Created by okunev on 21.10.2014.
 */
public class ReportSteps extends BaseReportSteps {

    @Step("Построить отчет 'таблица'")
    public StatV1DataGETSchema getTableReportAndExpectSuccess(IFormParameters... parameters) {
        return getJsonReportAndExpectSuccess(RequestTypes.TABLE, parameters);
    }

}
